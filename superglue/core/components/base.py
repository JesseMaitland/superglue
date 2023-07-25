import re
import boto3
import json
import botocore
from io import BytesIO
from pathlib import Path
from hashlib import md5
from abc import ABC, abstractmethod
from multiprocessing import Pool, cpu_count
from jinja2 import Environment, PackageLoader
from typing import Optional, Dict, Tuple, List, TypeVar, Generator
from superglue.environment.variables import SUPERGLUE_IAM_ROLE, SUPERGLUE_S3_BUCKET, SUPERGLUE_S3_PREFIX


BaseSuperglueComponentType = TypeVar(name="BaseSuperglueComponentType", bound="BaseSuperglueComponent")


class BaseSuperglueComponent(ABC):
    def __init__(self, root_dir: Path, component_name: str, component_type: str) -> None:

        self.root_dir = root_dir
        self.component_name = component_name
        self.component_type = component_type

    def __eq__(self, other: BaseSuperglueComponentType) -> bool:
        try:
            return self.component_name == other.component_name
        except AttributeError:
            return False

    @property
    def component_path(self) -> Path:
        return self.root_dir / self.component_name

    @staticmethod
    def get_jinja_environment() -> Environment:
        """
        used to get a jinja2 templating environment.
        Returns: Jinja2 Environment
        """
        loader = PackageLoader(package_name="superglue", package_path="templates")
        return Environment(loader=loader, trim_blocks=True, lstrip_blocks=True)

    @abstractmethod
    def save(self) -> None:
        pass


SuperglueComponentType = TypeVar("SuperglueComponentType", bound="SuperglueComponent")


class SuperglueComponent(BaseSuperglueComponent, ABC):

    version_pattern = r".*(version=[0-9]+).*"

    def __init__(
        self, bucket: Optional[str] = SUPERGLUE_S3_BUCKET, iam_role: Optional[str] = SUPERGLUE_IAM_ROLE, *args, **kwargs
    ) -> None:
        super(SuperglueComponent, self).__init__(*args, **kwargs)

        self.bucket = bucket
        self.iam_role = iam_role

        try:
            self.version = json.load(self.version_file.open())
        except FileNotFoundError:
            self.version = {}

        try:
            current_version = self.version.pop("version_number")
        except KeyError:
            current_version = 0

        self.version_number = current_version

    @property
    def name(self) -> str:
        return self.component_name

    @property
    def version_file(self) -> Path:
        return self.component_path / ".version"

    @property
    def s3_prefix_root(self) -> str:
        if SUPERGLUE_S3_PREFIX:
            return f"{SUPERGLUE_S3_PREFIX}/superglue"
        return f"superglue"

    @property
    def s3_path(self) -> str:
        return f"s3://{self.bucket}/{self.s3_prefix_root}/{self.component_type}/{self.component_name}/version={self.version_number}/{self.component_name}"

    @property
    def s3_prefix(self) -> str:
        return f"{self.s3_prefix_root}/{self.component_type}/{self.component_name}/version={self.version_number}"

    @property
    def s3_filter(self) -> str:
        return f"{self.s3_prefix_root}/{self.component_type}/{self.component_name}"

    @property
    def s3_version_path(self) -> str:
        return f"{self.s3_prefix}/{self.component_name}/.version"

    @property
    def is_locked(self) -> bool:
        return self.version == self.get_version_hashes()

    @property
    def is_unlocked(self) -> bool:
        return not self.is_locked

    @property
    def is_deployable(self) -> bool:
        s3_version = self.fetch_s3_version()
        local_version = self.version.copy()
        local_version["version_number"] = self.version_number
        return self.is_locked and local_version != s3_version

    @property
    def status(self) -> Tuple[str, str, str]:

        if self.version_in_sync:
            remote_version_message = "in sync"
        else:
            remote_version_message = "refresh required"

        if self.is_locked:
            locked_message = "locked"
        else:
            locked_message = "unlocked"

        if self.is_deployable:
            deployable_message = "out of sync"
        else:
            deployable_message = "in sync"

        return locked_message, deployable_message, remote_version_message

    @property
    def pretty_table_row(self) -> List[str]:
        return [self.component_name, self.component_type, *self.status, self.version_number]

    @property
    def next_version_number(self) -> int:
        return self.version_number + 1

    @property
    def version_in_sync(self) -> bool:
        remote_version = self.fetch_s3_version_number()
        return remote_version == self.version_number

    def increment_version(self) -> None:
        self.version_number += 1

    def component_files(self) -> List[Path]:
        file_list = []
        filters = [".DS_Store", ".empty", "__pycache__", ".zip"]

        for path in self.component_path.glob("**/*"):
            if path.is_file():
                filtered = False

                for part in path.parts:
                    if part in filters:
                        filtered = True

                if not filtered:
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
        filters = [
            ".version",
            "config_merged.yml",
        ]

        for path in self.component_files():
            if path.name not in filters and path.suffix != ".zip":
                key, digest = self.hash_file(path)
                version_hashes[key] = digest
        return version_hashes

    def save_version_file(self, version_number: Optional[int] = None) -> None:
        version_hashes = self.get_version_hashes()

        if not version_number:
            version_hashes["version_number"] = self.version_number
        else:
            version_hashes["version_number"] = version_number
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
            if code in ["Not Found", "Forbidden"]:
                return {}
            raise e

    def lock(self) -> None:
        self.save_version_file()

    def append_version(self) -> None:
        self.increment_version()
        self.save_version_file()

    @staticmethod
    def compare_previous(previous: int, current: int) -> int:
        return max(previous, current)

    def parse_version_numbers(self, keys):
        for key in keys:
            yield int(re.match(self.version_pattern, key).group(1).partition("=")[2])

    def list_superglue_components(self) -> Generator[List[str], None, None]:
        s3_client = boto3.client("s3")
        continue_token = "start"
        while continue_token:

            kwargs = {"Bucket": self.bucket, "Prefix": self.s3_filter}

            if continue_token and continue_token != "start":
                kwargs["ContinuationToken"] = continue_token

            results = s3_client.list_objects_v2(**kwargs)

            try:
                yield [key["Key"] for key in results["Contents"] if key["Key"]]
            except KeyError:
                yield []

            continue_token = results.get("ContinuationToken")

    def fetch_s3_version_number(self) -> int:
        v = 0
        for keys in self.list_superglue_components():
            for version in self.parse_version_numbers(keys):
                v = self.compare_previous(v, version)
        return int(v)

    @abstractmethod
    def deploy(self, increment_version: bool) -> None:
        pass

    @abstractmethod
    def delete(self) -> None:
        pass

    @abstractmethod
    def save(self) -> None:
        pass
