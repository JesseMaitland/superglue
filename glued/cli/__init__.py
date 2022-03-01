from argparse import ArgumentParser  # This is the standard library arg parser, and it works great.
from glued.cli import job
from glued.cli import project
from glued.cli import debug
from glued.cli import shared

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

    project_sync_command = project_command_subparser.add_parser('sync')
    project_sync_command.set_defaults(func=project.sync)

    # job commands
    job_command = sub_parser.add_parser('job')
    job_command_subparser = job_command.add_subparsers()

    # job new commands
    job_new_command = job_command_subparser.add_parser('new')
    job_new_command.set_defaults(func=job.new)
    job_new_command.add_argument('name')

    # job sync command
    job_sync_command = job_command_subparser.add_parser('deploy')
    job_sync_command.set_defaults(func=job.deploy)
    job_sync_command.add_argument('name')

    # job delete command
    job_delete_command = job_command_subparser.add_parser('delete')
    job_delete_command.set_defaults(func=job.delete)
    job_delete_command.add_argument('name')

    # debug
    debug_command = sub_parser.add_parser('debug')
    debug_command.set_defaults(func=debug.run)

    # shared commands
    shared_parser = sub_parser.add_parser('shared')
    shared_command_subparser = shared_parser.add_subparsers()

    # shared new command
    shared_new_command = shared_command_subparser.add_parser('new')
    shared_new_command.add_argument('name')
    shared_new_command.set_defaults(func=shared.new)

    # Parse the arguments passed into the program from the entry point.
    return parser.parse_args()
