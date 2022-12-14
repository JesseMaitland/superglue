import inspect
from typing import List, Optional
from argparse import Namespace
from superglue.core.project import SuperglueProject, SuperglueModule
from superglue.utils.cli import validate_account, expected_cli_args
from prettytable import PrettyTable
# from superglue.exceptions import JobNameValidationError
# from superglue.environment.variables import SUPERGLUE_IAM_ROLE
# from superglue.core._project import SuperGlueProject, SuperGlueJob, SuperGlueModule


__version__ = "0.3.2"


class CommandBase:

    def __init__(self, cli_args: Namespace) -> None:
        self.cli_args = cli_args
        self.project = SuperglueProject()

    @classmethod
    def commands(cls) -> List[str]:
        return [m[0] for m in inspect.getmembers(cls, inspect.isfunction) if m[0] != "__init__"]


class RootCommands(CommandBase):

    @staticmethod
    def version() -> None:
        print(f"The AWS Glue Deployment Utility -- superglue version :: {__version__}")

    @validate_account
    def account(self) -> None:
        pass

    def init(self) -> None:
        self.project.create()
        print("superglue project initialized!")

    def package(self) -> None:
        edited = self.project.modules.edited()
        if edited:
            for module in edited:
                module.package()
                print(f"Superglue module {module.module_name} has been successfully packaged!")
        else:
            print("No changes in superglue modules found. Nothing to package.")

    @validate_account
    def status(self) -> None:
        table = self.project.get_pretty_table()

        for module in self.project.modules:
            table.add_row(module.pretty_table_row)

        for job in self.project.jobs:
            table.add_row(job.pretty_table_row)

        print(table)

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
        pass


class JobCommands(CommandBase):

    def new(self) -> None:
        """
        Creates a new job in the glue_jobs directory
        """
        job = self.project.job.new(self.cli_args.name)
        job.save()
        print(f"created new glue job {self.cli_args.name}")
        exit()

    @validate_account
    def status(self) -> None:
        table = self.project.get_pretty_table()

        if self.cli_args.name:
            job = self.project.job.get(self.cli_args.name)
            table.add_row(job.pretty_table_row)
        else:
            for job in self.project.jobs:
                table.add_row(job.pretty_table_row)
        print(table)

    @expected_cli_args("name")
    def package(self) -> None:
        job = self.project.job.get(self.cli_args.name)
        for module in job.modules():
            module.package()
        job.commit()

    @expected_cli_args("name")
    def check(self) -> None:
        job = self.project.job.get(self.cli_args.name)
        job.render()
        job.save_deployment_config()

    @validate_account
    @expected_cli_args("name")
    def deploy(self) -> None:
        job = self.project.job.get(self.cli_args.name)
        modules = job.modules()

        for module in modules:
            if module.is_edited:
                module.package()

            if module.is_deployable:
                module.deploy()
        job.deploy()


class ModuleCommands(CommandBase):

    @expected_cli_args("name")
    def new(self) -> None:
        module = self.project.module.new(self.cli_args.name)
        module.save()
        print(f"created new superglue module {self.cli_args.name}")

    @validate_account
    def status(self) -> None:
        table = self.project.get_pretty_table()

        if self.cli_args.name:
            module = self.project.module.get(self.cli_args.name)
            table.add_row(module.pretty_table_row)
        else:
            for module in self.project.modules:
                table.add_row(module.pretty_table_row)
        print(table)

    @expected_cli_args("name")
    def package(self) -> None:
        module = self.project.module.get(self.cli_args.name)
        if module.is_edited:
            module.package()
        else:
            print(f"Superglue module {module.module_name} is up to date. Nothing to package!")

    @validate_account
    @expected_cli_args("name")
    def deploy(self) -> None:
        module = self.project.module.get(self.cli_args.name)
        if module.is_deployable:
            module.package()
            module.deploy()
        else:
            print(f"Superglue module {module.module_name} is up to date! Nothing to deploy")


