from argparse import ArgumentParser
from superglue.cli import commands
from superglue.cli.utils import get_commands


def parse_args():

    # This is the root node of the main parser tree.
    parser = ArgumentParser()
    sub_parser = parser.add_subparsers(dest="command")
    sub_parser.required = True

    # set parser for all root level actions in the format
    # superglue "action" <options>
    for command in get_commands(commands):
        p = sub_parser.add_parser(command.method(), help=command.help)
        for args, kwargs in command.args.items():
            p.add_argument(*args, **kwargs)
        p.set_defaults(command=command)
    return parser.parse_args()
