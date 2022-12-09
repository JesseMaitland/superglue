import inspect
from typing import List
from argparse import Namespace
from superglue.core.project import SuperglueProject
from superglue.helpers.cli import validate_account
from prettytable import PrettyTable
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

        for edited_module in self.project.edited_modules():
            edited_module.create_zip()
            edited_module.save_version_file()
            print(f"committed superglue module {edited_module.module_name}")


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

    def check(self) -> None:
        job = self.project.job.get(self.cmd_args.name)
        modules = [self.project.module.get(module_name) for module_name in job.superglue_modules]
        job = self.project.job.render(job, modules)
        self.project.save_deployment_config(job)

    def deploy(self) -> None:
        job = self.project.job.get(self.cmd_args.name)
        job.deploy()
        modules = [self.project.module.get(module_name) for module_name in job.superglue_modules]
        job = self.project.job.render(job, modules)

        for config in job.deployment_config["job_configs"]:
            self.project.job.create_or_update(config)


class ModuleCommands(CommandBase):

    def new(self) -> None:
        module = self.project.module.new(self.cmd_args.name)
        module.save()
        print(f"created new superglue module {self.cmd_args.name}")

    def commit(self) -> None:
        module = self.project.module.get(self.cmd_args.name)
        self.package()
        module.save_version_file()
        print(f"committed superglue module {self.cmd_args.name}")

    def status(self) -> None:
        table = PrettyTable()
        table.field_names = ["module", "local status", "remote status"]
        module = self.project.module.get(self.cmd_args.name)

        next_version = module.get_version_hashes()
        this_version = module.version
        local_status = "up to date"
        remote_status = "up to date"

        if next_version != this_version:
            local_status = "edited"

        table.add_row([module.module_name, local_status, remote_status])

        print(table)

    def package(self) -> None:
        module = self.project.module.get(self.cmd_args.name)
        module.create_zip()
        print(f"packaged glue module {self.cmd_args.name}")

    def deploy(self) -> None:
        module = self.project.module.get(self.cmd_args.name)
        module.deploy()
        print(f"deployed glue module {self.cmd_args.name}")


