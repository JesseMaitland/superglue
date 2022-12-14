import json
import yaml
import boto3
import zipfile
import botocore
import operator
from io import BytesIO
from pathlib import Path
from hashlib import md5
from prettytable import PrettyTable
from multiprocessing import Pool, cpu_count
from jinja2 import Environment, PackageLoader
from typing import Dict, List, Optional, Tuple, TypeVar, Type
from superglue.environment.config import JOBS_PATH, NOTEBOOKS_PATH, MODULES_PATH
from superglue.environment.variables import SUPERGLUE_S3_BUCKET, SUPERGLUE_IAM_ROLE

SuperglueJobType = TypeVar("SuperglueJobType", bound="SuperglueJob")
SuperglueModuleType = TypeVar("SuperglueModuleType", bound="SuperglueModule")
BaseSuperglueComponentType = TypeVar("BaseSuperglueComponentType", bound="BaseSuperglueComponent")


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

    def __eq__(self, other: BaseSuperglueComponentType) -> bool:
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
            self.save_version_file()
        return json.load(self.version_file.open())

    @property
    def s3_path(self) -> str:
        return f"s3://{self.bucket}/superglue/{self.component_type}/{self.component_name}"

    @property
    def s3_prefix(self) -> str:
        return f"superglue/{self.component_type}"

    @property
    def s3_version_path(self) -> str:
        return f"superglue/{self.component_type}/{self.component_name}/.version"

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
        return [self.component_name, self.component_type, *self.status]

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
        filters = [".DS_Store"]

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
        for path in self.files():
            if path.name != ".version":
                key, digest = self.hash_file(path)
                version_hashes[key] = digest
        return version_hashes

    def save_version_file(self) -> None:
        version_hashes = self.get_version_hashes()
        json.dump(version_hashes, self.version_file.open(mode="w"), indent=4)

    def upload_object_to_s3(self, path: Path) -> None:
        s3_client = boto3.client("s3")
        relative_path = self.get_relative_path(path)
        print(f"Uploading -- s3://{self.bucket}{self.s3_prefix}/{relative_path}")
        s3_client.upload_file(path.as_posix(), self.bucket, f"{self.s3_prefix}/{relative_path}")

    def sync(self) -> None:
        with Pool(cpu_count()) as pool:
            files = self.files()
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

    def deploy(self) -> None:
        raise NotImplementedError

    def delete(self) -> None:
        raise NotImplementedError

    def save(self, **kwargs) -> None:
        raise NotImplementedError


class SuperglueComponentList(list):

    def edited(self) -> List[BaseSuperglueComponentType]:
        return [c for c in self if c.is_edited]

    def deployable(self) -> List[BaseSuperglueComponentType]:
        return [c for c in self if c.is_deployable]


class SuperglueModule(BaseSuperglueComponent):

    def __init__(self, module_name: str):

        super(SuperglueModule, self).__init__(
            root_dir=MODULES_PATH,
            component_name=module_name,
            component_type="superglue_module",
            bucket=SUPERGLUE_S3_BUCKET,
            iam_role=SUPERGLUE_IAM_ROLE,

        )

    @property
    def module_name(self) -> str:
        return self.component_name

    @property
    def module_root_path(self) -> Path:
        return self.root_dir / self.module_name

    @property
    def module_inner_path(self) -> Path:
        return self.module_root_path / self.module_name

    @property
    def zipfile(self) -> Path:
        return self.module_root_path / f"{self.module_name}.zip"

    @property
    def s3_zipfile_path(self) -> str:
        relative_path = self.zipfile.relative_to(self.module_root_path)
        return f"{self.s3_path}/{relative_path}"

    @classmethod
    def new(cls, module_name: str) -> SuperglueModuleType:
        return cls(module_name)

    @classmethod
    def get(cls, module_name: str) -> SuperglueModuleType:
        sg_module = cls(module_name)
        if not sg_module.module_root_path.exists():
            raise FileNotFoundError(f"No superglue module {module_name} exists.")
        return sg_module

    def save(self) -> None:
        if not self.module_root_path.exists():
            self.module_inner_path.mkdir(parents=True, exist_ok=True)

            init_py = self.module_inner_path / "__init__.py"
            init_py.touch(exist_ok=True)
            self.save_version_file()
        else:
            print(f"shared python module {self.module_name} already exists.")

    def deploy(self) -> None:
        if self.is_deployable:
            self.sync()
            print(f"Superglue module {self.module_name} successfully deployed!")
        elif self.is_edited:
            print(f"Superglue module {self.module_name} has edits in progress. Please run superglue package")
        else:
            print(f"Superglue module {self.module_name} up to date in S3. Nothing to deploy.")

    def delete(self) -> None:
        pass

    def create_zip(self) -> None:
        with zipfile.ZipFile(self.zipfile, mode="w") as zip_file:
            for file in self.module_root_path.glob("**/*.py"):
                content = file.read_text()
                content = content.encode("utf-8")
                rel_path = file.relative_to(self.module_root_path).as_posix()
                zip_file.writestr(rel_path, content)

    def package(self) -> None:
        if self.is_edited:
            self.create_zip()
            self.save_version_file()
            print(f"Superglue module {self.module_name} has been successfully packaged!")
        else:
            print(f"Superglue module {self.module_name} package is up to date!")


class SuperglueJob(BaseSuperglueComponent):

    def __init__(self, job_name: str) -> None:

        super(SuperglueJob, self).__init__(
            root_dir=JOBS_PATH,
            component_name=job_name,
            component_type="superglue_job",
            bucket=SUPERGLUE_S3_BUCKET,
            iam_role=SUPERGLUE_IAM_ROLE,

        )

        try:
            self.config: Dict = yaml.safe_load(self.config_file.open())
        except FileNotFoundError:
            self.config = {}

        self.deployment_config = {"job_configs": []}

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
    def shared_path(self) -> Path:
        return MODULES_PATH

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
    def deployment_config_file(self) -> Path:
        return self.job_path / "deployment.yml"

    @property
    def superglue_modules(self) -> List[str]:
        return self.config["superglue_modules"]

    @property
    def overrides(self) -> List[Dict]:
        try:
            return yaml.safe_load(self.overrides_file.open())["overrides"]
        except FileNotFoundError:
            return []

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
            return [p for e in ext for p in self.pys_path.glob(f"**/{e}")]
        except FileNotFoundError:
            return []

    @property
    def s3_main_script_path(self) -> str:
        return f"{self.s3_path}/main.py"

    @property
    def s3_py_paths(self) -> List[str]:
        py_s3_paths = []
        for py_file in self.py_files:
            relative_path = py_file.relative_to(self.job_path)
            py_s3_path = f"{self.s3_path}/{relative_path}"
            py_s3_paths.append(py_s3_path)
        return py_s3_paths

    @property
    def s3_jar_paths(self) -> List[str]:
        jar_s3_paths = []
        for jar_file in self.jar_files:
            relative_path = jar_file.relative_to(self.job_path)
            jar_s3_path = f"{self.s3_path}/{relative_path}"
            jar_s3_paths.append(jar_s3_path)
        return jar_s3_paths

    @classmethod
    def new(cls, job_name: str) -> SuperglueJobType:
        return cls(job_name)

    @classmethod
    def get(cls, job_name: str) -> SuperglueJobType:
        job = cls(job_name)
        if not job.job_path.exists():
            raise FileNotFoundError(f"Glue job with name {job_name} not found.")
        return job

    def render(self) -> None:
        extra_file_args = self.get_extra_file_args()
        modules = self.modules()
        config = self.config.copy()

        s3_module_paths = ",".join([module.s3_zipfile_path for module in modules])

        if s3_module_paths:
            try:
                xpfa = extra_file_args["--extra-py-files"]
                extra_file_args["--extra-py-files"] = f"{xpfa},{s3_module_paths}"
            except KeyError:
                extra_file_args["--extra-py-files"] = s3_module_paths

        config["job_config"]["DefaultArguments"].update(**extra_file_args)

        for override in self.overrides:
            config_override = config.copy()["job_config"]
            default_args = config_override["DefaultArguments"].copy()

            config_override.update(**override)
            config_override["DefaultArguments"].update(**default_args)
            self.deployment_config["job_configs"].append(config_override)

    def create_or_update(self) -> None:
        glue_client = boto3.client("glue")

        for config in self.deployment_config["job_configs"]:
            try:
                # check if the glue job exists
                job_exists = glue_client.get_job(JobName=config["Name"])

            except botocore.exceptions.ClientError:
                # the job does not exist, set to None to create it.
                print(f"the job {config['Name']} does not exist. It will be created")
                job_exists = None

            if job_exists:  # then update the job definition
                print(f"the job {config['Name']} exists. It will be updated")
                # create and update glue api have different parameters for job name, so pop the name param
                # out of our config and pass it to the 'JobName' parameter of the update api.
                params = config.copy()
                job_name = params.pop("Name")

                # request a job update, if it fails a client exception is raised.
                _ = glue_client.update_job(JobName=job_name, JobUpdate=params)

            else:
                # otherwise create the job for the first time
                # if it fails a client exception is raised.
                _ = glue_client.create_job(**config)

    def modules(self) -> SuperglueComponentList:
        return SuperglueComponentList(SuperglueModule.get(n) for n in self.superglue_modules)

    def get_extra_file_args(self) -> Dict[str, str]:
        extra_file_args = {}

        if self.s3_py_paths:
            s3_py_path_str = ",".join(self.s3_py_paths)
            extra_file_args["--extra-py-files"] = s3_py_path_str

        if self.s3_jar_paths:
            s3_jar_path_str = ",".join(self.s3_jar_paths)
            extra_file_args["--extra-jars"] = s3_jar_path_str

        return extra_file_args

    def deploy(self) -> None:
        if self.is_deployable:
            self.render()
            self.package()
            self.sync()
            self.create_or_update()
            print(f"Successfully deployed superglue job {self.job_name}")
        elif self.is_edited:
            print(f"Superglue job {self.job_name} has edits in progress. Please run superglue package")
        else:
            print(f"Superglue job {self.job_name} up to date in S3. Nothing to deploy.")

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
            print(f"created new glue job {self.job_name}")
        else:
            print(f"The job {self.job_path.name} already exists.")

    def save_deployment_config(self) -> None:
        self.deployment_config_file.touch(exist_ok=True)
        yaml.dump(
            self.deployment_config,
            self.deployment_config_file.open(mode="w"),
            Dumper=_NoAnchorsDumper
        )
        print(f"deployment config saved for superglue job {self.job_name}")

    def package(self) -> None:
        self.render()
        self.save_deployment_config()
        self.save_version_file()
        print(f"committed superglue job {self.job_name}")


class _NoAnchorsDumper(yaml.SafeDumper):
    def ignore_aliases(self, data):
        return True


class SuperglueProject:
    """Class represents the superglue project structure"""

    def __init__(self) -> None:
        self.makefile_template = Path(__file__).parent.parent / "templates" / "makefile"

    @property
    def jobs_path(self) -> Path:
        return JOBS_PATH

    @property
    def modules_path(self) -> Path:
        return MODULES_PATH

    @property
    def notebooks_path(self) -> Path:
        return NOTEBOOKS_PATH

    @property
    def job(self) -> Type[SuperglueJob]:
        return SuperglueJob

    @property
    def jobs(self) -> SuperglueComponentList[SuperglueJob]:
        jobs = [self.job.get(p.name) for p in self.jobs_path.iterdir()]
        return SuperglueComponentList(jobs)

    @property
    def module(self) -> Type[SuperglueModule]:
        return SuperglueModule

    @property
    def modules(self) -> SuperglueComponentList[SuperglueModule]:
        modules = [self.module.get(p.name) for p in self.modules_path.iterdir()]
        return SuperglueComponentList(modules)

    @property
    def pretty_table_fields(self) -> List[str]:
        return ["Component Name", "Component Type", "Local Stats", "s3 Status"]

    def create(self) -> None:
        self.jobs_path.mkdir(exist_ok=True)
        self.modules_path.mkdir(exist_ok=True)
        self.notebooks_path.mkdir(exist_ok=True)

        makefile = Path.cwd() / "makefile"

        if makefile.exists():
            makefile = Path.cwd() / "makefile.sg"

        if not makefile.exists():
            content = self.makefile_template.read_text()
            makefile.touch()
            makefile.write_text(content)

    def included_modules(self, job: SuperglueJob) -> SuperglueComponentList:
        modules = [self.module.get(name) for name in job.superglue_modules]
        return SuperglueComponentList(modules)

    def get_pretty_table(self) -> PrettyTable:
        table = PrettyTable()
        table.field_names = self.pretty_table_fields
        table.sort_key = operator.itemgetter(0, 1)
        table.sortby = "Component Type"
        for field in self.pretty_table_fields:
            table.align[field] = "l"
        return table
