from superglue.cli import parse_args
from dotenv import load_dotenv


def main() -> None:
    """
    main entry point for the spam command line tool.
    """
    load_dotenv()
    cmd_args = parse_args()
    commands = cmd_args.command(cmd_args=cmd_args)
    method = getattr(commands, cmd_args.method)
    method()



if __name__ == "__main__":
    """
    This is here to allow execution by referencing the project directory instead of a .py file.
    """
    main()
