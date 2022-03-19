import boto3
import json
from io import BytesIO
from pathlib import Path
from hashlib import md5
from typing import List, Tuple, Dict
from multiprocessing import Pool, cpu_count
from glued.environment.variables import DEFAULT_S3_BUCKET


class BaseFileController:
    def __init__(
        self,
        parent_dir: Path,
        dir_name: str,
        bucket_prefix: str,
        bucket: str = DEFAULT_S3_BUCKET,
    ) -> None:
        self.parent_dir = parent_dir
        self.dir_name = dir_name
        self.bucket_prefix = bucket_prefix
        self.bucket = bucket
        self.dir_path = self.parent_dir / self.dir_name

    @property
    def version_file(self) -> Path:
        return self.parent_dir / self.dir_name / ".version"

    @property
    def version(self) -> Dict:
        return json.load(self.version_file.open())

    @property
    def hashable_files(self) -> List[Path]:
        return [
            path
            for path in self.list_all_files()
            if path.name not in (".version", ".DS_Store")
        ]

    @property
    def s3_prefix(self) -> str:
        return f"s3://{self.bucket}/{self.bucket_prefix}"

    def _upload_object_to_s3(self, path: Path) -> None:

        s3_client = boto3.client("s3")

        key = self._get_key(path)
        s3_client.upload_file(
            path.as_posix(), self.bucket, f"{self.bucket_prefix}/{key}"
        )

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

    def fetch_s3_version(self) -> Dict[str, str]:
        s3_client = boto3.client("s3")
        key = self._get_key(self.version_file)
        with BytesIO() as buffer:
            s3_client.download_fileobj(
                self.bucket, f"{self.bucket_prefix}/{key}", buffer
            )
            buffer.seek(0)
            return json.load(buffer)

    def delete(self) -> None:
        raise NotImplementedError

    def deploy(self) -> None:
        self.sync()
