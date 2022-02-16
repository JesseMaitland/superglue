import boto3
import json
from pathlib import Path
from hashlib import md5
from typing import List, Tuple, Dict
from multiprocessing import Pool, cpu_count
from botocore.client import BaseClient
from io import BytesIO
from glued.environment import DEFAULT_S3_BUCKET


class GluedJob:

    def __init__(self,
                 parent_dir: Path,
                 job_name: str,
                 bucket: str = DEFAULT_S3_BUCKET,
                 glue_client: BaseClient = None,
                 s3_client: BaseClient = None) -> None:

        self.parent_dir = parent_dir
        self.job_name = job_name
        self.bucket = bucket
        self.glue_client = glue_client
        self.s3_client = s3_client

    @property
    def job_path(self) -> Path:
        return self.parent_dir / self.job_name

    @property
    def py_files_path(self) -> Path:
        return self.job_path / 'py'

    @property
    def jars_path(self) -> Path:
        return self.job_path / 'jars'

    @property
    def version_file(self) -> Path:
        return self.job_path / '.version'

    @property
    def version(self) -> Dict:
        return json.load(self.version_file.open())

    @property
    def hashable_files(self) -> List[Path]:
        return [path for path in self.list_job_files() if path.name != '.version']

    def _upload_object_to_s3(self, path: Path) -> None:

        s3_client = boto3.client('s3')

        with path.open(mode='rb') as data:
            key = self._get_key(path)
            s3_client.upload_fileobj(data, self.bucket, f"glue_jobs/{key}")

    def _get_key(self, path: Path) -> str:
        return path.relative_to(self.parent_dir).as_posix()

    def _hash_file(self, path: Path) -> Tuple[str, str]:
        key = self._get_key(path)

        md5_hash = md5()
        with path.open('rb') as data:
            for chunk in iter(lambda: data.read(4096), b""):
                md5_hash.update(chunk)
            return key, md5_hash.hexdigest()

    def _save_version(self, version_hashes: Dict) -> None:
        json.dump(version_hashes, self.version_file.open(mode='w'), indent=4)

    def _get_version_hashes(self) -> Dict[str, str]:
        version_hashes = {}
        for path in self.hashable_files:
            key, digest = self._hash_file(path)
            version_hashes[key] = digest
        return version_hashes

    def create(self, config_template: str, script_template: str) -> None:

        if not self.job_path.exists():

            self.job_path.mkdir(exist_ok=True)
            self.py_files_path.mkdir(exist_ok=True)
            self.jars_path.mkdir(exist_ok=True)

            config_path = self.job_path / 'config.yml'
            config_path.touch(exist_ok=True)
            config_path.write_text(config_template)

            script_path = self.job_path / 'main.py'
            script_path.touch(exist_ok=True)
            script_path.write_text(script_template)

            self.version_file.touch(exist_ok=True)
            version_hashes = self._get_version_hashes()
            self._save_version(version_hashes)

        else:
            print(f'The job {self.job_path.name} already exists.')

    def sync_job(self) -> None:
        with Pool(cpu_count()) as pool:
            files = self.list_job_files()
            pool.map(self._upload_object_to_s3, files)

    def list_job_files(self) -> List[Path]:
        return [path for path in self.job_path.glob('**/*.*') if path.is_file()]

    def create_version(self) -> None:
        version_hashes = self._get_version_hashes()
        self._save_version(version_hashes)

    def fetch_s3_version(self) -> Dict[str, str]:
        s3_client = boto3.client('s3')
        key = self._get_key(self.version_file)
        with BytesIO() as buffer:
            s3_client.download_fileobj(self.bucket, f"glue_jobs/{key}", buffer)
            buffer.seek(0)
            return json.load(buffer)
