from superglue.cli.command import Command
from superglue.cli.utils import get_parser_name, validate_account


parser_name = get_parser_name(__name__)
cli_help = "--> Interact with superglue modules"


class BaseArgs:

    args = {
        ("-n", "--name"): {
            "help": "Name of the superglue module (directory)"
        }
    }


class New(BaseArgs, Command):

    help = "--> Create a new superglue module to share across superglue jobs."

    def __call__(self) -> None:
        module = self.project.module.new(self.cli_args.name)
        module.save()


class Status(Command):

    help = "--> Print the status of all superglue modules."

    @validate_account
    def __call__(self) -> None:
        table = self.project.get_pretty_table()

        for module in self.project.modules:
            table.add_row(module.pretty_table_row)

        print(table)


class Package(Command):

    help = "--> Packages superglue modules which have changed since the last issued package command"

    def __call__(self) -> None:
        if self.project.modules.edited():
            for module in self.project.modules.edited():
                module.package()
        else:
            print("Superglue modules are up to date. Nothing to package!")


class Deploy(BaseArgs, Command):

    help = "--> Manually deploy a superglue module. Modules must first be up to date using the package command."

    @validate_account
    def __call__(self) -> None:
        module = self.project.module.get(self.cli_args.name)
        module.deploy()
