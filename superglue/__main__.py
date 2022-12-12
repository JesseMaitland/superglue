from superglue.cli import parse_args
from dotenv import load_dotenv


def main() -> None:
    """
    main entry point for the spam command line tool.
    """
    load_dotenv()
    cli_args = parse_args()
    commands = cli_args.command(cli_args=cli_args)
    method = getattr(commands, cli_args.method)
    method()


if __name__ == "__main__":
    """
    This is here to allow execution by referencing the project directory instead of a .py file.
    """
    main()
