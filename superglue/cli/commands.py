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


class CommandBase:
    pass


class JobCommands(CommandBase):


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


