import boto3
import json
from pathlib import Path
from hashlib import md5
from typing import List, Tuple, Dict
from multiprocessing import Pool, cpu_count
from botocore.client import BaseClient
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
    def extra_py_files_path(self) -> Path:
        return self.job_path / 'py'

    @property
    def extra_jars_path(self) -> Path:
        return self.job_path / 'jars'

    @property
    def extra_jars_s3_path(self) -> str:
        return f"{self.bucket}/jars/"

    @property
    def extra_py_files_s3_path(self) -> str:
        return f"{self.bucket}/py_files/"

    @property
    def py_files(self) -> List[Path]:
        try:
            return [path for path in self.extra_py_files_path.glob('*.py')]
        except FileNotFoundError:
            return []

    @property
    def jar_files(self) -> List[Path]:
        try:
            return [path for path in self.extra_jars_path.glob('*.jar')]
        except FileNotFoundError:
            return []

    @property
    def extra_jar_keys(self) -> List[str]:
        return [f"/jars/{jar}" for jar in self.jar_files]

    @property
    def extra_py_file_keys(self) -> List[str]:
        return [f"/py_files/{py_file}" for py_file in self.py_files]

    @property
    def version_file(self) -> Path:
        return self.job_path / '.version'

    @property
    def version(self) -> Dict:
        return json.load(self.version_file)

    def _upload_object_to_s3(self, path: Path) -> None:

        s3_client = boto3.client('s3')

        with path.open(mode='rb') as data:
            key = self._get_key(path)
            s3_client.upload_fileobj(data, self.bucket, f"glue_jobs/{key}")

    def _get_key(self, path: Path) -> str:
        return path.relative_to(self.parent_dir).as_posix()

    def _get_digest(self, path: Path) -> Tuple[str, str]:
        key = self._get_key(path)

        md5_hash = md5()
        with path.open('rb') as data:
            for chunk in iter(lambda: data.read(4096), b""):
                md5_hash.update(chunk)
            return key, md5_hash.hexdigest()

    def _save_version(self, data: Dict) -> None:
        json.dump(data, self.version_file.open(mode='w'), indent=4)

    def create(self, config_template: str, script_template: str) -> None:
        self.job_path.mkdir(exist_ok=True)
        self.extra_py_files_path.mkdir(exist_ok=True)
        self.extra_jars_path.mkdir(exist_ok=True)

        config_path = self.job_path / 'config.yml'
        config_path.touch(exist_ok=True)
        config_path.write_text(config_template)

        script_path = self.job_path / 'main.py'
        script_path.touch(exist_ok=True)
        script_path.write_text(script_template)

        self.version_file.touch(exist_ok=True)

        files_to_digest = [path for path in self.list_files() if path.name != '.version']

        version_hashes = {}
        for path in files_to_digest:
            key, digest = self._get_digest(path)
            version_hashes[key] = digest

        print(version_hashes)
        self._save_version(version_hashes)

    def sync_job(self) -> None:
        with Pool(cpu_count()) as pool:
            files = self.list_files()
            pool.map(self._upload_object_to_s3, files)

    def list_files(self) -> List[Path]:
        return [path for path in self.job_path.glob('**/*.*') if path.is_file()]

    def create_version(self) -> None:
        pass
