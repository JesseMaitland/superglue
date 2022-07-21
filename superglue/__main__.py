from superglue.cli import parse_args
from dotenv import load_dotenv


def main() -> None:
    """
    main entry point for the spam command line tool.
    """
    load_dotenv()
    cmd = parse_args()
    cmd.func(cmd)


if __name__ == "__main__":
    """
    This is here to allow execution by referencing the project directory instead of a .py file.
    """
    main()
