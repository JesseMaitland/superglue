from argparse import ArgumentParser
from glued.cli import job
from glued.cli import project
from glued.cli import module
from glued.cli import version
from glued.cli.validaton_actions import ValidateJobCommandName


def parse_args():

    # This is the root node of the main parser tree.
    parser = ArgumentParser()
    sub_parser = parser.add_subparsers(dest="command")
    sub_parser.required = True

    # version
    version_command = sub_parser.add_parser("version")
    version_command.set_defaults(func=version.print_version)

    # project commands
    project_command = sub_parser.add_parser("project")
    project_command_subparser = project_command.add_subparsers()

    project_init_command = project_command_subparser.add_parser("init")
    project_init_command.set_defaults(func=project.init)

    project_sync_command = project_command_subparser.add_parser("sync")
    project_sync_command.set_defaults(func=project.sync)

    project_status_command = project_command_subparser.add_parser("status")
    project_status_command.set_defaults(func=project.status)

    # job commands
    job_command = sub_parser.add_parser("job")
    job_command_subparser = job_command.add_subparsers()
    job_command.add_argument("name", action=ValidateJobCommandName)

    # job new commands
    job_new_command = job_command_subparser.add_parser("new")
    job_new_command.set_defaults(func=job.new)

    job_sync_command = job_command_subparser.add_parser("deploy")
    job_sync_command.set_defaults(func=job.deploy)

    job_delete_command = job_command_subparser.add_parser("delete")
    job_delete_command.set_defaults(func=job.delete)

    job_check_command = job_command_subparser.add_parser("check")
    job_check_command.set_defaults(func=job.check)

    # module commands
    module_parser = sub_parser.add_parser("module")
    module_command_subparser = module_parser.add_subparsers()

    # shared new command
    module_new_command = module_command_subparser.add_parser("new")
    module_new_command.add_argument("name")
    module_new_command.set_defaults(func=module.new)

    module_build_command = module_command_subparser.add_parser("build")
    module_build_command.add_argument("name", help="name of module to build or 'all'")

    module_build_command.set_defaults(func=module.build)

    # Parse the arguments passed into the program from the entry point.
    return parser.parse_args()
