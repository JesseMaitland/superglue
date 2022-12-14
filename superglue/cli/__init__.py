from argparse import ArgumentParser
from superglue.cli import job
from superglue.cli import module
from superglue.cli.validation import ValidateJobCommandName, ValidateModuleCommandName
from superglue.cli.commands import RootCommands, JobCommands, ModuleCommands


def parse_args():

    # This is the root node of the main parser tree.
    parser = ArgumentParser()
    sub_parser = parser.add_subparsers(dest="command")
    sub_parser.required = True

    for root_command in RootCommands.commands():
        p = sub_parser.add_parser(root_command)
        p.set_defaults(command=RootCommands, method=root_command)

    job_command_parser = sub_parser.add_parser("job")
    job_command_subparser = job_command_parser.add_subparsers()

    for job_command in JobCommands.commands():
        p = job_command_subparser.add_parser(job_command)
        p.add_argument("-n", "--name")
        p.set_defaults(command=JobCommands, method=job_command)

    module_command_parser = sub_parser.add_parser("module")
    module_command_subparser = module_command_parser.add_subparsers()

    for module_command in ModuleCommands.commands():
        p = module_command_subparser.add_parser(module_command)
        p.add_argument("-n", "--name")
        p.set_defaults(command=ModuleCommands, method=module_command)

    return parser.parse_args()
