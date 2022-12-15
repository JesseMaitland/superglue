from superglue.cli import parse_args
from dotenv import load_dotenv


def main() -> None:

    load_dotenv()
    cli_args = parse_args()
    command = cli_args.command(cli_args=cli_args)
    command()


if __name__ == "__main__":
    print("foo")
    """
    This is here to allow execution by referencing the project directory instead of a .py file.
    """
    main()
