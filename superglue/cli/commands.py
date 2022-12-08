import inspect
from typing import List
from argparse import Namespace
from superglue.core.project import SuperglueProject
from superglue.helpers.cli import validate_account
# from superglue.exceptions import JobNameValidationError
# from superglue.environment.variables import SUPERGLUE_IAM_ROLE
# from superglue.core._project import SuperGlueProject, SuperGlueJob, SuperGlueModule


__version__ = "0.3.2"


class CommandBase:

    def __init__(self, cmd_args: Namespace) -> None:
        self.cmd_args = cmd_args
        self.project = SuperglueProject()

    @classmethod
    def commands(cls) -> List[str]:
        return [m[0] for m in inspect.getmembers(cls, inspect.isfunction) if m[0] != "__init__"]


class RootCommands(CommandBase):

    def version(self) -> None:
        print(f"superglue -- the aws glue job deployment utility -- version :: {__version__}")

    def init(self) -> None:
        self.project.create()
        print("superglue project initialized!")

    @validate_account
    def status(self) -> None:

        stale_jobs = [j.job_name for j in self.project.list_stale_jobs()]
        stale_modules = [m.module_name for m in self.project.list_stale_modules()]

        if stale_jobs or stale_modules:
            print("The superglue project is not up to date.")

            if stale_jobs:
                print(f"The following jobs need to be committed {stale_jobs}")

            if stale_modules:
                print(f"The following modules need to be committed {stale_modules}")

            exit(1)
        else:
            print("local superglue project is fresh as a daisy!")

    @validate_account
    def deploy(self) -> None:
        jobs_to_sync = self.project.list_jobs_to_sync()

        for job in jobs_to_sync:
            print(f"deploying job {job.job_name}")
            job.deploy()

        modules_to_sync = self.project.list_modules_to_sync()

        for module in modules_to_sync:
            print(f"deploying module {module.module_name}")
            module.create_zip()
            module.deploy()

    def commit(self) -> None:

        for stale_job in self.project.list_stale_jobs():
            stale_job.create_version()

        for stale_module in self.project.list_stale_modules():
            stale_module.create_version()


class JobCommands(CommandBase):

    def new(self) -> None:
        """
        Creates a new job in the glue_jobs directory
        """
        job = self.project.job.new(self.cmd_args.name)
        job.save()
        print(f"created new glue job {self.cmd_args.name}")
        exit()

    def commit(self) -> None:
        job = self.project.job.get(self.cmd_args.name)
        job.save_version_file()
        print(f"committed glue job {self.cmd_args.name}")
        exit()
