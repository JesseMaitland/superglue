import boto3
import yaml
import botocore
import json
import copy
import zipfile
from pathlib import Path
from typing import List
from superglue.exceptions import JobNameValidationError
from superglue.environment.variables import SUPERGLUE_S3_BUCKET, SUPERGLUE_JOB_PREFIX, SUPERGLUE_JOB_SUFFIX
from superglue.core.fileio import BaseFileIO


class SuperGlueJob(BaseFileIO):
    """
    Class represents a superglue job definition.
    """

    def __init__(self, parent_dir: Path, job_name: str, bucket: str = SUPERGLUE_S3_BUCKET) -> None:

        super().__init__(
            parent_dir=parent_dir,
            dir_name=job_name,
            bucket=bucket,
            bucket_prefix="glue_jobs",
        )

        self.job_name = job_name
        self.shared_dir = self.parent_dir / "shared"
        self.check_dir = self.parent_dir / self.job_name / "check"
        self.override_file = self.parent_dir / self.job_name / "overrides.yml"
        self.shared_paths = []
        self.config = {}
        self.overrides = []

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

    def _validate_name_prefix(self) -> None:
        if SUPERGLUE_JOB_PREFIX:
            if not self.job_name.startswith(SUPERGLUE_JOB_PREFIX):
                raise JobNameValidationError(f"The job name must have prefix {SUPERGLUE_JOB_PREFIX}")

    def _validate_name_suffix(self) -> None:
        if SUPERGLUE_JOB_SUFFIX:
            if not self.job_name.endswith(SUPERGLUE_JOB_SUFFIX):
                raise JobNameValidationError(f"The job name must have suffix {SUPERGLUE_JOB_SUFFIX}")

    def validate_name(self) -> None:
        self._validate_name_prefix()
        self._validate_name_suffix()

    def create(self, iam_role: str, job_name: str, script_location: str, override: bool = False) -> None:

        if not self.job_path.exists():

            self._set_template_env()

            script_content = self.templates.get_template("main.template.py").render()
            config_content = self.templates.get_template("job_config.template.yml").render(
                iam_role=iam_role, job_name=job_name, script_location=script_location
            )

            self.job_path.mkdir(exist_ok=True)
            self.py_files_path.mkdir(exist_ok=True)
            self.jars_path.mkdir(exist_ok=True)

            self.config_path.touch(exist_ok=True)
            self.config_path.write_text(config_content)

            self.script_path.touch(exist_ok=True)
            self.script_path.write_text(script_content)

            self.version_file.touch(exist_ok=True)

            if override:
                self.override_file.touch(exist_ok=True)

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

        if self.override_file.exists():
            self.load_overrides()

    def load_overrides(self) -> None:
        overrides = yaml.safe_load(self.override_file.open())
        self.overrides = overrides["overrides"]

    def instantiate_overridden_jobs(self) -> List["SuperGlueJob"]:
        jobs = []
        for override in self.overrides:
            job = copy.deepcopy(self)

            py_files = job.config["DefaultArguments"].get("--extra-py-files")
            jar_files = job.config["DefaultArguments"].get("--extra-jars")

            job.config.update(**override)
            job.job_name = job.config["Name"]

            if py_files:
                job.config["DefaultArguments"]["--extra-py-files"] = py_files

            if jar_files:
                job.config["DefaultArguments"]["--extra-jars"] = jar_files

            job.validate_name()
            jobs.append(job)
        return jobs

    def dump_config(self) -> None:
        check_file = self.check_dir / f"{self.job_name}__config.json"
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


class SuperGlueModule(BaseFileIO):
    def __init__(self, parent_dir: Path, module_name: str, bucket: str = SUPERGLUE_S3_BUCKET):
        self.module_name = module_name
        self.root_module = parent_dir / module_name
        self.module_path = parent_dir / module_name / module_name
        self.zip_path = self.root_module / f"{self.module_name}.zip"
        self.relative_root = Path.cwd()

        super(SuperGlueModule, self).__init__(
            parent_dir=parent_dir,
            dir_name=module_name,
            bucket_prefix="shared",
            bucket=bucket,
        )

    def create(self) -> None:
        if not self.module_path.exists():
            self.module_path.mkdir(parents=True, exist_ok=True)

            init_py = self.module_path / "__init__.py"
            init_py.touch(exist_ok=True)
        else:
            print(f"shared python module {self.module_name} already exists.")

    def delete(self) -> None:
        pass

    def create_zip(self) -> None:
        with zipfile.ZipFile(self.zip_path, mode="w") as zip_file:
            for file in self.module_path.glob("**/*.py"):
                content = file.read_text()
                content = content.encode("utf-8")
                rel_path = file.relative_to(self.root_module).as_posix()
                zip_file.writestr(rel_path, content)


class SuperGlueProject:
    """Class represents the superglue project structure"""

    def __init__(self) -> None:
        self.jobs_root = Path.cwd() / "glue_jobs"
        self.shared_root = Path.cwd() / "shared"
        self.notebooks = Path.cwd() / "notebooks"
        self.makefile_template = Path(__file__).parent.parent / "templates" / "makefile"

    def create(self) -> None:
        self.jobs_root.mkdir(exist_ok=True)
        self.shared_root.mkdir(exist_ok=True)
        self.notebooks.mkdir(exist_ok=True)

        makefile = Path.cwd() / "makefile"

        if makefile.exists():
            makefile = Path.cwd() / "makefile.sg"

        if not makefile.exists():
            content = self.makefile_template.read_text()
            makefile.touch()
            makefile.write_text(content)

    def list_job_names(self) -> List[str]:
        return [path.name for path in self.jobs_root.iterdir() if path.is_dir()]

    def list_jobs(self) -> List[SuperGlueJob]:
        jobs = []

        for path in self.jobs_root.iterdir():
            job = SuperGlueJob(self.jobs_root, path.name)
            job.load_config()

            if job.overrides:
                for overridden_job in job.instantiate_overridden_jobs():
                    jobs.append(overridden_job)
            else:
                jobs.append(job)

        return jobs

    def list_modules(self) -> List[SuperGlueModule]:
        modules = []

        for path in self.shared_root.iterdir():
            if path.name != ".DS_Store":
                module = SuperGlueModule(self.shared_root, path.name)
                modules.append(module)
        return modules

    def list_stale_jobs(self) -> List[SuperGlueJob]:
        stale_jobs = []

        for superglue_job in self.list_jobs():
            if not superglue_job.overrides:
                superglue_job.load_config()

            if superglue_job.version != superglue_job.get_next_version():
                stale_jobs.append(superglue_job)

        return stale_jobs

    def list_stale_modules(self) -> List[SuperGlueModule]:
        stale_modules = []
        for superglue_module in self.list_modules():

            if superglue_module.version != superglue_module.get_next_version():
                stale_modules.append(superglue_module)

        return stale_modules

    def list_jobs_to_sync(self) -> List[SuperGlueJob]:
        jobs_to_sync = []

        for job in self.list_jobs():
            if not job.overrides:
                job.load_config()
                job.create_version()

            local_version = job.version
            remote_version = job.fetch_s3_version()

            if local_version != remote_version:
                print(f"{job.job_name} differs from the job currently in S3.")
                jobs_to_sync.append(job)

        return jobs_to_sync

    def list_modules_to_sync(self) -> List[SuperGlueModule]:

        modules_to_sync = []

        for superglue_module in self.list_modules():
            superglue_module.create_version()
            local_version = superglue_module.version

            try:
                remote_version = superglue_module.fetch_s3_version()
            except botocore.exceptions.ClientError:
                print("no remote version found")
                remote_version = None

            if local_version != remote_version:
                print(f"{superglue_module.module_name} differs from the job currently in S3.")
                modules_to_sync.append(superglue_module)
        return modules_to_sync
