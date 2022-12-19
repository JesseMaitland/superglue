import boto3
import json
import botocore
from io import BytesIO
from pathlib import Path
from hashlib import md5
from abc import ABC, abstractmethod
from multiprocessing import Pool, cpu_count
from jinja2 import Environment, PackageLoader
from typing import Optional, Dict, Tuple, List
from superglue.core.types import SuperglueComponentType
from superglue.environment.variables import SUPERGLUE_IAM_ROLE, SUPERGLUE_S3_BUCKET


class SuperglueComponent(ABC):
    def __init__(
        self,
        root_dir: Path,
        component_name: str,
        component_type: str,
        version_number: Optional[int] = None,
        bucket: Optional[str] = SUPERGLUE_S3_BUCKET,
        iam_role: Optional[str] = SUPERGLUE_IAM_ROLE,
    ) -> None:

        self.root_dir = root_dir
        self.component_name = component_name
        self.component_type = component_type
        self.bucket = bucket
        self.iam_role = iam_role
        self._version_number = version_number

    def __eq__(self, other: SuperglueComponentType) -> bool:
        try:
            return self.component_name == other.component_name
        except AttributeError:
            return False

    @property
    def component_path(self) -> Path:
        return self.root_dir / self.component_name

    @property
    def version_file(self) -> Path:
        return self.component_path / ".version"

    @property
    def version(self) -> Dict:
        if not self.version_file.exists():
            self.save_version_file(increment_version=False)
        return json.load(self.version_file.open())

    @property
    def version_number(self) -> int:
        if self._version_number:
            return self._version_number
        return self.version.get("version_number", 0)

    @property
    def next_version_number(self) -> int:
        return self.version_number + 1

    @property
    def s3_path(self) -> str:
        return f"s3://{self.bucket}/superglue/{self.component_type}/{self.component_name}/version={self.version_number}"

    @property
    def s3_prefix(self) -> str:
        return f"superglue/{self.component_type}/{self.component_name}/version={self.version_number}"

    @property
    def s3_version_path(self) -> str:
        return f"{self.s3_prefix}/{self.component_name}/.version"

    @property
    def is_edited(self) -> bool:
        return self.version != self.get_version_hashes()

    @property
    def is_deployable(self) -> bool:
        return self.is_edited is False and self.version != self.fetch_s3_version()

    @property
    def status(self) -> Tuple[str, str]:

        if self.is_edited:
            return "edits in progress", "out of sync"

        elif self.is_deployable:
            return "up to date", "out of sync"

        else:
            return "up to date", "in sync"

    @property
    def pretty_table_row(self) -> List[str]:
        return [self.component_name, self.component_type, *self.status, self.version_number]

    @staticmethod
    def get_jinja_environment() -> Environment:
        """
        used to get a jinja2 templating environment.
        Returns: Jinja2 Environment
        """
        loader = PackageLoader(package_name="superglue", package_path="templates")
        return Environment(loader=loader, trim_blocks=True, lstrip_blocks=True)

    def component_files(self) -> List[Path]:
        file_list = []
        filters = [".DS_Store", ".empty"]

        for path in self.component_path.glob("**/*"):
            if path.is_file() and path.name not in filters:
                file_list.append(path)
        return file_list

    def get_relative_path(self, path: Path) -> str:
        return path.relative_to(self.root_dir).as_posix()

    def hash_file(self, path: Path) -> Tuple[str, str]:

        relative_path = self.get_relative_path(path)
        md5_hash = md5()

        with path.open("rb") as data:
            for chunk in iter(lambda: data.read(4096), b""):
                md5_hash.update(chunk)
            return relative_path, md5_hash.hexdigest()

    def get_version_hashes(self) -> Dict[str, str]:
        version_hashes = {}
        for path in self.component_files():
            if path.name != ".version":
                key, digest = self.hash_file(path)
                version_hashes[key] = digest
        return version_hashes

    def save_version_file(self, increment_version: Optional[bool] = True) -> None:
        version_hashes = self.get_version_hashes()

        if increment_version:
            version_hashes["version_number"] = self.next_version_number
        else:
            version_hashes["version_number"] = 0

        json.dump(version_hashes, self.version_file.open(mode="w"), indent=4)

    def upload_object_to_s3(self, path: Path) -> None:
        s3_client = boto3.client("s3")
        relative_path = self.get_relative_path(path)
        print(f"Uploading -- s3://{self.bucket}/{self.s3_prefix}/{relative_path}")
        s3_client.upload_file(path.as_posix(), self.bucket, f"{self.s3_prefix}/{relative_path}")

    def sync(self) -> None:
        with Pool(cpu_count()) as pool:
            files = self.component_files()
            pool.map(self.upload_object_to_s3, files)

    def fetch_s3_version(self) -> Dict[str, str]:
        s3_client = boto3.client("s3")
        try:
            with BytesIO() as buffer:
                s3_client.download_fileobj(self.bucket, self.s3_version_path, buffer)
                buffer.seek(0)
                return json.load(buffer)
        except botocore.exceptions.ClientError as e:
            code = e.args[0].partition(":")[2].strip()
            if code == "Not Found":
                return {}
            raise e

    @abstractmethod
    def deploy(self) -> None:
        pass

    @abstractmethod
    def delete(self) -> None:
        pass

    @abstractmethod
    def save(self) -> None:
        pass
