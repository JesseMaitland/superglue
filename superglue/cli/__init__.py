from argparse import ArgumentParser
from superglue.cli import root, job, module
from superglue.cli.utils import get_commands


def parse_args():

    # This is the root node of the main parser tree.
    parser = ArgumentParser()
    sub_parser = parser.add_subparsers(dest="command")
    sub_parser.required = True

    # set parser for all root level actions in the format
    # superglue "action" <options>
    for command in get_commands(root):
        p = sub_parser.add_parser(command.method(), help=command.help)
        for args, kwargs in command.args.items():
            p.add_argument(*args, **kwargs)
        p.set_defaults(command=command)

    # set subparser commands
    for commands in job, module:
        command_parser = sub_parser.add_parser(commands.parser_name, help=commands.cli_help)
        command_subparser = command_parser.add_subparsers()

        for command in get_commands(commands):
            p = command_subparser.add_parser(command.method(), help=command.help)
            for args, kwargs in command.args.items():
                p.add_argument(*args, **kwargs)
            p.set_defaults(command=command)

    # job_command_parser = sub_parser.add_parser("job")
    # job_command_subparser = job_command_parser.add_subparsers()
    # for command in job.commands():
    #     p = job_command_subparser.add_parser(command.method)
    #     for key, value in command.args.items():
    #         p.add_argument(*key, **value)
    #     p.set_defaults(command=command, method=command.method)

    # for job_command in JobCommands.commands():
    #     p = job_command_subparser.add_parser(job_command)
    #     p.add_argument("-n", "--name")
    #     p.set_defaults(command=JobCommands, method=job_command)

    # module_command_parser = sub_parser.add_parser("module")
    # module_command_subparser = module_command_parser.add_subparsers()
    #
    # for module_command in ModuleCommands.commands():
    #     p = module_command_subparser.add_parser(module_command)
    #     p.add_argument("-n", "--name")
    #     p.set_defaults(command=ModuleCommands, method=module_command)

    return parser.parse_args()
