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


class ModuleCommands(CommandBase):


    @validate_account
    @expected_cli_args("name")
    def deploy(self) -> None:
        module = self.project.module.get(self.cli_args.name)
        if module.is_deployable:
            module.package()
            module.deploy()
        else:
            print(f"Superglue module {module.module_name} is up to date! Nothing to deploy")


