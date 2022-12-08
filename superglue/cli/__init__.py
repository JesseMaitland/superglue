from argparse import ArgumentParser
from superglue.cli import job
from superglue.cli import module
from superglue.cli.validation import ValidateJobCommandName, ValidateModuleCommandName
from superglue.cli.commands import RootCommands, JobCommands


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
        p.add_argument("-n", "--name", required=True)
        p.set_defaults(command=JobCommands, method=job_command)

    # job commands
    # job_parser = sub_parser.add_parser("job")
    # job_parser.add_argument()
    # job_command_subparser = job_command.add_subparsers()
    # job_command.add_argument("name", action=ValidateJobCommandName)
    # job_command.add_argument(
    #     "--override", "-o", action="store_true", default=False, help="set this flag to create an overrides.yml file"
    # )

    # job new commands
    # job_new_command = job_command_subparser.add_parser("new")
    # job_new_command.set_defaults(func=job.new)
#
    # job_sync_command = job_command_subparser.add_parser("deploy")
    # job_sync_command.set_defaults(func=job.deploy)
#
    # job_delete_command = job_command_subparser.add_parser("delete")
    # job_delete_command.set_defaults(func=job.delete)
#
    # job_check_command = job_command_subparser.add_parser("check")
    # job_check_command.set_defaults(func=job.check)

    ## module commands
    #module_parser = sub_parser.add_parser("module")
    #module_command_subparser = module_parser.add_subparsers()
    #module_parser.add_argument("name", action=ValidateModuleCommandName)
#
    ## module new command
    #module_new_command = module_command_subparser.add_parser("new")
    #module_new_command.set_defaults(func=module.new)
#
    ## module build command
    #module_build_command = module_command_subparser.add_parser("build")
    #module_build_command.set_defaults(func=module.build)

    # Parse the arguments passed into the program from the entry point.
    return parser.parse_args()
