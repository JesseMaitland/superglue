import boto3
import botocore
import json
import yaml
import copy
import zipfile
from io import BytesIO
from pathlib import Path
from hashlib import md5
from multiprocessing import Pool, cpu_count
from typing import Dict, List, Optional, Tuple, TypeVar, Type
from jinja2 import Environment, PackageLoader
from superglue.environment.config import JOBS_PATH, NOTEBOOKS_PATH, SHARED_PATH
from superglue.environment.variables import SUPERGLUE_S3_BUCKET, SUPERGLUE_IAM_ROLE


class BaseSuperglueComponent:
    """Base file controller used to control base level file access"""

    def __init__(
            self,
            root_dir: Path,
            component_name: str,
            component_type: str,

            bucket: Optional[str] = SUPERGLUE_S3_BUCKET,
            iam_role: Optional[str] = SUPERGLUE_IAM_ROLE
    ) -> None:

        self.root_dir = root_dir
        self.component_name = component_name
        self.component_type = component_type
        self.bucket = bucket
        self.iam_role = iam_role

    @property
    def component_path(self) -> Path:
        return self.root_dir / self.component_name

    @property
    def version_file(self) -> Path:
        return self.component_path / ".version"

    @property
    def version(self) -> Dict:
        return json.load(self.version_file.open())

    @property
    def s3_path(self) -> str:
        return f"s3://{self.bucket}/superglue/{self.component_type}/{self.component_name}"

    @property
    def s3_prefix(self) -> str:
        return f"/superglue/{self.component_type}/{self.component_name}"

    @staticmethod
    def get_jinja_environment() -> Environment:
        """
        used to get a jinja2 templating environment.
        Returns: Jinja2 Environment
        """
        loader = PackageLoader(package_name="superglue", package_path="templates")
        return Environment(loader=loader, trim_blocks=True, lstrip_blocks=True)

    def files(self) -> List[Path]:
        file_list = []
        filters = (".version", ".DS_Store")

        for path in self.component_path.glob("**/*"):
            if path.is_file() and path.name not in filters and path.suffix != ".zip":
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
        for path in self.files():
            key, digest = self.hash_file(path)
            version_hashes[key] = digest
        return version_hashes

    def save_version_file(self) -> None:
        version_hashes = self.get_version_hashes()
        json.dump(version_hashes, self.version_file.open(mode="w"), indent=4)

    def upload_object_to_s3(self, path: Path) -> None:
        s3_client = boto3.client("s3")
        relative_path = self.get_relative_path(path)
        s3_client.upload_file(path.as_posix(), self.bucket, f"{self.s3_prefix}/{relative_path}")

    def sync(self) -> None:
        with Pool(cpu_count()) as pool:
            files = self.files()
            pool.map(self.upload_object_to_s3, files)

    def fetch_s3_version(self) -> Dict[str, str]:
        s3_client = boto3.client("s3")
        try:
            with BytesIO() as buffer:
                s3_client.download_fileobj(self.bucket, f"{self.s3_prefix}/.version", buffer)
                buffer.seek(0)
                return json.load(buffer)
        except botocore.exceptions.ClientError:
            return {}

    def deploy(self) -> None:
        self.sync()

    def delete(self) -> None:
        raise NotImplementedError

    def save(self, **kwargs) -> None:
        raise NotImplementedError


SuperglueJobType = TypeVar("SuperglueJobType", bound="SuperglueJob")


class SuperglueJob(BaseSuperglueComponent):

    def __init__(self, job_name: str) -> None:

        super(SuperglueJob, self).__init__(
            root_dir=JOBS_PATH,
            component_name=job_name,
            component_type="superglue_job",
            bucket=SUPERGLUE_S3_BUCKET,
            iam_role=SUPERGLUE_IAM_ROLE,

        )

    @property
    def job_name(self) -> str:
        return self.component_name

    @property
    def job_path(self) -> Path:
        return self.root_dir / self.job_name

    @property
    def check_path(self) -> Path:
        return self.job_path / "check"

    @property
    def pys_path(self) -> Path:
        return self.job_path / "py"

    @property
    def jars_path(self) -> Path:
        return self.job_path / "jars"

    @property
    def main_script_file(self) -> Path:
        return self.job_path / "main.py"

    @property
    def config_file(self) -> Path:
        return self.job_path / "config.yml"

    @property
    def overrides_file(self) -> Path:
        return self.job_path / "overrides.yml"

    @property
    def s3_main_script_path(self) -> str:
        return f"{self.s3_prefix}/main.py"

    @property
    def overrides(self) -> List[Dict]:
        try:
            return yaml.safe_load(self.overrides_file.open())["overrides"]
        except FileNotFoundError:
            return []

    @classmethod
    def new(cls, job_name: str) -> SuperglueJobType:
        return cls(job_name=job_name)

    @classmethod
    def get(cls, job_name: str) -> SuperglueJobType:
        job = cls(job_name=job_name)
        if not job.job_path.exists():
            raise FileNotFoundError(f"Glue job with name {job_name} not found.")
        return job

    def delete(self) -> None:
        pass

    def save(self, **kwargs) -> None:

        if not self.job_path.exists():

            self.job_path.mkdir(exist_ok=True)
            self.pys_path.mkdir(exist_ok=True)
            self.jars_path.mkdir(exist_ok=True)

            jinja = self.get_jinja_environment()

            # set config content
            config_template = jinja.get_template("job_config.template.yml")
            config_content = config_template.render(
                iam_role=self.iam_role,
                job_name=self.job_name,
                s3_main_script_path=self.s3_main_script_path
            )

            self.config_file.touch(exist_ok=True)
            self.config_file.write_text(config_content)

            # set main script content
            main_script_template = jinja.get_template("main.template.py")
            main_script_content = main_script_template.render()

            self.main_script_file.touch(exist_ok=True)
            self.main_script_file.write_text(main_script_content)

            self.version_file.touch(exist_ok=True)
            self.overrides_file.touch(exist_ok=True)

            self.save_version_file()

        else:
            print(f"The job {self.job_path.name} already exists.")


class SuperglueProject:
    """Class represents the superglue project structure"""

    def __init__(self) -> None:
        self.makefile_template = Path(__file__).parent.parent / "templates" / "makefile"

    @property
    def jobs_path(self) -> Path:
        return JOBS_PATH

    @property
    def shared_path(self) -> Path:
        return SHARED_PATH

    @property
    def notebooks_path(self) -> Path:
        return NOTEBOOKS_PATH

    @property
    def job(self) -> Type[SuperglueJob]:
        return SuperglueJob

    @property
    def jobs(self) -> List:
        for path in self.jobs_path.iterdir():
            job = self.

    def create(self) -> None:
        self.jobs_path.mkdir(exist_ok=True)
        self.shared_path.mkdir(exist_ok=True)
        self.notebooks_path.mkdir(exist_ok=True)

        makefile = Path.cwd() / "makefile"

        if makefile.exists():
            makefile = Path.cwd() / "makefile.sg"

        if not makefile.exists():
            content = self.makefile_template.read_text()
            makefile.touch()
            makefile.write_text(content)
