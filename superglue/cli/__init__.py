from argparse import ArgumentParser
from superglue.cli import job
from superglue.cli import project
from superglue.cli import module
from superglue.cli import version
from superglue.cli.validation import ValidateJobCommandName, ValidateModuleCommandName


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

    project_sync_command = project_command_subparser.add_parser("deploy")
    project_sync_command.set_defaults(func=project.deploy)

    project_status_command = project_command_subparser.add_parser("status")
    project_status_command.add_argument("--remote", "-r", action="store_true", default=False, dest="remote")
    project_status_command.set_defaults(func=project.status)

    project_commit_command = project_command_subparser.add_parser("commit")
    project_commit_command.set_defaults(func=project.commit)

    # job commands
    job_command = sub_parser.add_parser("job")
    job_command_subparser = job_command.add_subparsers()
    job_command.add_argument("name", action=ValidateJobCommandName)
    job_command.add_argument(
        "--override", "-o", action="store_true", default=False, help="set this flag to create an overrides.yml file"
    )

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
    module_parser.add_argument("name", action=ValidateModuleCommandName)

    # module new command
    module_new_command = module_command_subparser.add_parser("new")
    module_new_command.set_defaults(func=module.new)

    # module build command
    module_build_command = module_command_subparser.add_parser("build")
    module_build_command.set_defaults(func=module.build)

    # Parse the arguments passed into the program from the entry point.
    return parser.parse_args()
