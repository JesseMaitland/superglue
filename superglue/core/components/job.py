import os
import yaml
import boto3
import botocore
from io import StringIO
from pathlib import Path
from typing import Dict, List, Optional, TypeVar
from superglue.core.components.module import SuperglueModule
from superglue.core.components.base import SuperglueComponent
from superglue.environment.config import JOBS_PATH, MODULES_PATH
from superglue.core.components.component_list import SuperglueComponentList
from superglue.environment.variables import SUPERGLUE_S3_BUCKET, SUPERGLUE_IAM_ROLE
from superglue.core.components.tests import SuperglueTests


SuperglueJobType = TypeVar("SuperglueJobType", bound="SuperglueJob")


class NoAnchorsDumper(yaml.SafeDumper):
    def ignore_aliases(self, data):
        return True


class SuperglueJob(SuperglueComponent):
    def __init__(self, job_name: str, tests: Optional[SuperglueTests] = None, *args, **kwargs) -> None:
        self.tests = tests or SuperglueTests()

        super(SuperglueJob, self).__init__(
            *args,
            root_dir=JOBS_PATH,
            component_name=job_name,
            component_type="superglue_job",
            bucket=SUPERGLUE_S3_BUCKET,
            iam_role=SUPERGLUE_IAM_ROLE,
            **kwargs,
        )

        try:
            config_context = os.path.expandvars(self.config_file.read_text())
            self.config: Dict = yaml.safe_load(StringIO(config_context))
        except FileNotFoundError:
            self.config = {}

        self.deployment_config = {"job_configs": []}

    @property
    def job_path(self) -> Path:
        return self.root_dir / self.name

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
    def job_test_path(self) -> Path:
        return self.tests.jobs_test_dir / self.name

    @property
    def job_tests_file(self) -> Path:
        return self.job_test_path / f"test_{self.name}.py"

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
    def superglue_modules(self) -> Dict[str, str]:
        return self.config.get("superglue_modules", {})

    @property
    def overrides(self) -> List[Dict]:
        try:
            return yaml.safe_load(self.overrides_file.open())["overrides"]
        except FileNotFoundError:
            pass
        except TypeError:
            pass
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
        config["job_config"]["Command"]["ScriptLocation"] = self.s3_main_script_path

        if self.overrides:
            for override in self.overrides:
                config_override = config.copy()["job_config"]
                default_args = config_override["DefaultArguments"].copy()

                config_override.update(**override)
                config_override["DefaultArguments"].update(**default_args)
                self.deployment_config["job_configs"].append(config_override.copy())
        else:
            self.deployment_config["job_configs"].append(self.config.copy()["job_config"])

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
        component_list = SuperglueComponentList()
        for name, meta in self.superglue_modules.items():
            module = SuperglueModule.from_version(module_name=name, version_number=int(meta["version_number"]))
            component_list.append(module)
        return component_list

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
        self.generate_deployment_yml()
        self.sync()
        self.create_or_update()

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
                iam_role=self.iam_role, job_name=self.name, s3_main_script_path=self.s3_main_script_path
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
            self.save_tests()

    def save_deployment_config(self) -> None:
        self.deployment_config_file.touch(exist_ok=True)
        yaml.dump(self.deployment_config, self.deployment_config_file.open(mode="w"), Dumper=NoAnchorsDumper)

    def generate_deployment_yml(self) -> None:
        if self.deployment_config_file.exists():
            self.deployment_config_file.unlink()
        self.render()
        self.save_deployment_config()

    def save_tests(self) -> None:
        jinja = self.get_jinja_environment()
        test_template = jinja.get_template("job_test.template.py.txt")
        test_content = test_template.render(job=self.name)

        self.job_test_path.mkdir(parents=True, exist_ok=True)
        self.job_tests_file.touch(exist_ok=True)
        self.job_tests_file.write_text(test_content)
