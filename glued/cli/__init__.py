from argparse import ArgumentParser  # This is the standard library arg parser, and it works great.
from glued.cli import job
from glued.cli import project
from glued.cli import debug

def parse_args():

    # This is the root node of the main parser tree.
    parser = ArgumentParser()
    sub_parser = parser.add_subparsers(dest='command')
    sub_parser.required = True

    # project commands
    project_command = sub_parser.add_parser('project')
    project_command_subparser = project_command.add_subparsers()

    # project new commands
    project_init_command = project_command_subparser.add_parser('init')
    project_init_command.set_defaults(func=project.init)

    # job commands
    job_command = sub_parser.add_parser('job')
    job_command_subparser = job_command.add_subparsers()

    # job new commands
    job_new_command = job_command_subparser.add_parser('new')
    job_new_command.set_defaults(func=job.new)
    job_new_command.add_argument('name')

    job_sync_command = job_command_subparser.add_parser('sync')
    job_sync_command.set_defaults(func=job.sync)
    job_sync_command.add_argument('name')

    # debug
    debug_command = sub_parser.add_parser('debug')
    debug_command.set_defaults(func=debug.run)

    # Parse the arguments passed into the program from the entry point.
    return parser.parse_args()
