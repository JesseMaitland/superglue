import boto3
import yaml
import botocore
import json
from pathlib import Path
from typing import List
from glued.environment.variables import GLUED_S3_BUCKET
from glued.core.base_file_controller import BaseFileController


class GluedJob(BaseFileController):
    def __init__(self, parent_dir: Path, job_name: str, bucket: str = GLUED_S3_BUCKET) -> None:

        super().__init__(
            parent_dir=parent_dir,
            dir_name=job_name,
            bucket=bucket,
            bucket_prefix="glue_jobs",
        )

        self.job_name = job_name
        self.shared_dir = self.parent_dir / "shared"
        self.check_dir = self.parent_dir / self.job_name / "check"
        self.shared_paths = []
        self.config = {}

    @property
    def s3_job_path(self) -> str:
        return f"{self.s3_prefix}/{self.job_name}"

    @property
    def s3_script_path(self) -> str:
        return f"{self.s3_job_path}/main.py"

    @property
    def job_path(self) -> Path:
        return self.parent_dir / self.job_name

    @property
    def py_files_path(self) -> Path:
        return self.job_path / "py"

    @property
    def jars_path(self) -> Path:
        return self.job_path / "jars"

    @property
    def config_path(self) -> Path:
        return self.job_path / "config.yml"

    @property
    def script_path(self) -> Path:
        return self.job_path / "main.py"

    @property
    def jar_files(self) -> List[Path]:
        try:
            return [p for p in self.jars_path.glob("**/*.jar")]
        except FileNotFoundError:
            return []

    @property
    def py_files(self) -> List[Path]:
        ext = ["*.py", "*.jar"]
        try:
            return [p for e in ext for p in self.py_files_path.glob(f"**/{e}")]
        except FileNotFoundError:
            return []

    def _format_file_s3_path(self, path: Path) -> str:
        key = Path(self._get_key(path))
        key_str = "/".join(key.parts[-2:])
        return f"{self.s3_job_path}/{key_str}"

    def _format_shared_s3_path(self, path: Path) -> str:
        key = self._get_key(path)
        return f"s3://{self.bucket}/{key}"

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
            print(f"The job {self.job_path.name} already exists.")

    def load_config(self) -> None:

        config = yaml.safe_load(self.config_path.open())
        self.config = config["job_config"]

        shared = config.get("shared", [])

        self.shared_paths = []

        for s in shared:
            path = self.shared_dir / s / f"{s}.zip"
            path = self._format_shared_s3_path(path)
            self.shared_paths.append(path)

        shared_py_files_str = ",".join(self.shared_paths)

        py_files_str = ",".join([self._format_file_s3_path(p) for p in self.py_files])
        jar_files_str = ",".join([self._format_file_s3_path(p) for p in self.jar_files])

        # no spaces allowed
        py_files_str = py_files_str.replace(" ", "")
        jar_files_str = jar_files_str.replace(" ", "")

        if shared_py_files_str:
            py_files_str = f"{py_files_str},{shared_py_files_str}"

        if py_files_str.startswith(", "):
            py_files_str = py_files_str.lstrip(", ")

        if py_files_str:
            self.config["DefaultArguments"]["--extra-py-files"] = py_files_str

        if jar_files_str:
            self.config["DefaultArguments"]["--extra-jars"] = jar_files_str

    def dump_config(self) -> None:
        check_file = self.check_dir / "payload.json"
        self.check_dir.mkdir(exist_ok=True)
        json.dump(self.config, check_file.open(mode="w+"), indent=4, sort_keys=True)

    def create_or_update_job(self) -> None:
        glue_client = boto3.client("glue")

        try:
            # check if the glue job exists
            job_exists = glue_client.get_job(JobName=self.config["Name"])

        except botocore.exceptions.ClientError:
            # the job does not exist, set to None to create it.
            job_exists = None

        if job_exists:  # then update the job definition

            # create and update glue api have different parameters for job name, so pop the name param
            # out of our config and pass it to the 'JobName' parameter of the update api.
            params = self.config.copy()
            job_name = params.pop("Name")

            # request a job update, if it fails a client exception is raised.
            _ = glue_client.update_job(JobName=job_name, JobUpdate=params)

        else:
            # otherwise create the job for the first time
            # if it fails a client exception is raised.
            _ = glue_client.create_job(**self.config)

    def delete_job_files(self) -> None:
        s3_client = boto3.client("s3")
        object_paths = s3_client.list_objects_v2(Bucket=self.bucket, Prefix=f"glue_jobs/{self.job_name}")

        try:
            object_paths = [path["Key"] for path in object_paths["Contents"]]
        except KeyError:
            return

        to_delete = {"Objects": [{"Key": path} for path in object_paths]}
        _ = s3_client.delete_objects(Bucket=self.bucket, Delete=to_delete)

    def delete_glue_job(self) -> None:
        glue_client = boto3.client("glue")
        glue_client.delete_job(JobName=self.config["Name"])

    def delete(self) -> None:
        self.delete_job_files()
        self.delete_glue_job()

    def deploy(self) -> None:
        self.sync()
        self.create_or_update_job()
