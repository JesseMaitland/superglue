from argparse import Namespace

# set the version number, which is manged by symantic release process
__version__ = '0.1.0'


def print_version(cmd: Namespace) -> None:
    print(__version__)
