import inspect
from typing import List, Optional
from argparse import Namespace
from superglue.exceptions import DeploymentError
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
        else:
            print("No changes in superglue modules found. Nothing to package.")

        edited = self.project.jobs.edited()

        if edited:
            for job in edited:
                job.package()
        else:
            print("No changes in superglue jobs found. Nothing to package.")

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
        if self.cli_args.package:
            print("Packaging before deployment")
            for module in self.project.modules.edited():
                module.package()

            for job in self.project.jobs.edited():
                job.package()
        else:
            if self.project.modules.edited() or self.project.jobs.edited():
                print("Active edits in progress. Please run superglue package before attempting deployment")
                exit(1)

        deployable_modules = self.project.modules.deployable()
        if deployable_modules:
            for module in deployable_modules:
                module.deploy()
        else:
            print("All superglue modules are up to date in S3. Nothing to deploy.")

        deployable_jobs = self.project.jobs.deployable()

        if deployable_jobs:
            for job in deployable_jobs:
                job.deploy()
        else:
            print("All superglue jobs are up to date in S3. Nothing to deploy.")


class JobCommands(CommandBase):

    def new(self) -> None:
        job = self.project.job.new(self.cli_args.name)
        job.save()

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
        job.package()

    @expected_cli_args("name")
    def check(self) -> None:
        job = self.project.job.get(self.cli_args.name)
        job.render()
        job.save_deployment_config()

    @validate_account
    @expected_cli_args("name")
    def deploy(self) -> None:
        job = self.project.job.get(self.cli_args.name)

        for module in job.modules():
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


