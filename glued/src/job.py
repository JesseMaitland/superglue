import boto3
import json
import yaml
import botocore
from io import BytesIO
from pathlib import Path
from hashlib import md5
from typing import List, Tuple, Dict
from multiprocessing import Pool, cpu_count
from glued.environment import DEFAULT_S3_BUCKET


class GluedJob:

    def __init__(self,
                 parent_dir: Path,
                 job_name: str,
                 bucket: str = DEFAULT_S3_BUCKET) -> None:

        self.parent_dir = parent_dir
        self.job_name = job_name
        self.bucket = bucket
        self.config = {}

    @property
    def s3_job_path(self) -> str:
        return f"s3://{self.bucket}/glue_jobs"

    @property
    def s3_script_path(self) -> str:
        return f"{self.s3_job_path}/{self.job_name}/main.py"

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

    @property
    def config_path(self) -> Path:
        return self.job_path / 'config.yml'

    @property
    def script_path(self) -> Path:
        return self.job_path / 'main.py'

    @property
    def jar_files(self) -> List[Path]:
        try:
            return [p for p in self.jars_path.glob('**/*.jar')]
        except FileNotFoundError:
            return []

    @property
    def py_files(self) -> List[Path]:
        try:
            return [p for p in self.py_files_path.glob('**/*.py')]
        except FileNotFoundError:
            return []

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

    def _format_file_s3_path(self, path: Path) -> str:
        key = self._get_key(path)
        return f"{self.s3_job_path}/{key}"

    def create(self, config_template: str, script_template: str) -> None:

        if not self.job_path.exists():

            self.job_path.mkdir(exist_ok=True)
            self.py_files_path.mkdir(exist_ok=True)
            self.jars_path.mkdir(exist_ok=True)

            self.config_path.touch(exist_ok=True)
            self.config_path.write_text(config_template)

            self.script_path.touch(exist_ok=True)
            self.script_path.write_text(script_template)

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

    def load_config(self) -> None:
        try:
            self.config = yaml.safe_load(self.config_path.open())['job_config']
            py_files_str = ', '.join([self._format_file_s3_path(p) for p in self.py_files])
            jar_files_str = ', '.join([self._format_file_s3_path(p) for p in self.jar_files])

            if py_files_str:
                self.config['DefaultArguments']['--extra-py-files'] = py_files_str

            if jar_files_str:
                self.config['DefaultArguments']['--extra-jars'] = jar_files_str

        except TypeError:
            print('TypeError loading job config.yml Check config and try again')
            exit()
        except FileNotFoundError:
            print('FileNotFoundError while loading config.yml Check that config.yml exists in the job dir')
            exit()

    def create_or_update_job(self) -> None:
        glue_client = boto3.client('glue')

        try:
            # check if the glue job exists
            job_exists = glue_client.get_job(JobName=self.config['Name'])

        except botocore.exceptions.ClientError:
            # the job does not exist, set to None to create it.
            job_exists = None

        if job_exists:  # then update the job definition

            # create and update glue api have different parameters for job name, so pop the name param
            # out of our config and pass it to the 'JobName' parameter of the update api.
            params = self.config.copy()
            job_name = params.pop('Name')

            # request a job update, if it fails a client exception is raised.
            glue_response = glue_client.update_job(JobName=job_name, JobUpdate=params)
            request_type = 'update'

        else:  # otherwise create the job for the first time
            # request create job, if it fails a client exception is raised.
            glue_response = glue_client.create_job(**self.config)
            request_type = 'create'

