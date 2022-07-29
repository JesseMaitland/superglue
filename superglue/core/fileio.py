import boto3
import botocore
import json
from io import BytesIO
from pathlib import Path
from hashlib import md5
from typing import List, Tuple, Dict
from multiprocessing import Pool, cpu_count
from jinja2 import Environment, PackageLoader, Template
from superglue.environment.variables import SUPERGLUE_S3_BUCKET


class BaseFileIO:
    """Base file controller used to control base level file access"""

    def __init__(self, parent_dir: Path, dir_name: str, bucket_prefix: str, bucket: str = SUPERGLUE_S3_BUCKET) -> None:

        self.parent_dir = parent_dir
        self.dir_name = dir_name
        self.bucket_prefix = bucket_prefix
        self.bucket = bucket
        self.dir_path = self.parent_dir / self.dir_name
        self.templates = None

    @property
    def version_file(self) -> Path:
        return self.parent_dir / self.dir_name / ".version"

    @property
    def version(self) -> Dict:
        return json.load(self.version_file.open())

    @property
    def hashable_files(self) -> List[Path]:
        paths = []
        filters = ("__pycache__", ".version", ".DS_Store")

        for path in self.list_all_files():
            parts = path.as_posix().split("/")

            check = [f for f in filters if f in parts]
            if not check and ".zip" != path.suffix:
                paths.append(path)
        return paths

    @property
    def s3_prefix(self) -> str:
        return f"s3://{self.bucket}/{self.bucket_prefix}"

    def _upload_object_to_s3(self, path: Path) -> None:

        s3_client = boto3.client("s3")
        key = self._get_key(path)
        s3_client.upload_file(path.as_posix(), self.bucket, f"{self.bucket_prefix}/{key}")

    def _get_key(self, path: Path) -> str:
        return path.relative_to(self.parent_dir).as_posix()

    def _hash_file(self, path: Path) -> Tuple[str, str]:

        key = self._get_key(path)
        md5_hash = md5()

        with path.open("rb") as data:
            for chunk in iter(lambda: data.read(4096), b""):
                md5_hash.update(chunk)
            return key, md5_hash.hexdigest()

    def _save_version(self, version_hashes: Dict) -> None:
        json.dump(version_hashes, self.version_file.open(mode="w"), indent=4)

    def _get_version_hashes(self) -> Dict[str, str]:
        version_hashes = {}
        for path in self.hashable_files:
            key, digest = self._hash_file(path)
            version_hashes[key] = digest
        return version_hashes

    def create(self, **kwargs) -> None:
        raise NotImplementedError

    def sync(self) -> None:
        with Pool(cpu_count()) as pool:
            files = self.list_all_files()
            pool.map(self._upload_object_to_s3, files)

    def list_all_files(self) -> List[Path]:
        return [path for path in self.dir_path.glob("**/*") if path.is_file()]

    def create_version(self) -> None:
        version_hashes = self._get_version_hashes()
        self._save_version(version_hashes)

    def get_next_version(self) -> Dict[str, str]:
        return self._get_version_hashes()

    def fetch_s3_version(self) -> Dict[str, str]:
        s3_client = boto3.client("s3")
        key = self._get_key(self.version_file)
        try:
            with BytesIO() as buffer:
                s3_client.download_fileobj(self.bucket, f"{self.bucket_prefix}/{key}", buffer)
                buffer.seek(0)
                return json.load(buffer)
        except botocore.exceptions.ClientError:
            return {}

    def delete(self) -> None:
        raise NotImplementedError

    def deploy(self) -> None:
        self.sync()

    def _set_template_env(self) -> None:
        self.templates = TemplateIO()


class TemplateIO:
    def __init__(self) -> None:
        self.jina_env = self.get_jinja_environment()

    def get_template(self, template_name: str) -> Template:
        return self.jina_env.get_template(template_name)

    @staticmethod
    def get_jinja_environment() -> Environment:
        """
        used to get a jinja2 templating environment.
        Returns: Jinja2 Environment
        """
        loader = PackageLoader(package_name="superglue", package_path="templates")
        return Environment(loader=loader, trim_blocks=True, lstrip_blocks=True)
