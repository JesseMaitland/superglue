import boto3
from typing import Callable, Any
from superglue.environment.variables import SUPERGLUE_AWS_ACCOUNT


def validate_account(func: Callable) -> Callable:
    def wrapper(*args, **kwargs) -> Any:
        sts = boto3.client("sts")
        account_id = int(sts.get_caller_identity()["Account"])

        if account_id != SUPERGLUE_AWS_ACCOUNT:
            print(f"superglue expects account {SUPERGLUE_AWS_ACCOUNT} but account is {account_id}")
            exit(1)
        print(f"\n -- Using AWS Account {SUPERGLUE_AWS_ACCOUNT} --")
        return func(*args, **kwargs)

    return wrapper


def yes_no_confirmation(msg: str) -> None:

    while True:

        selection = input(f"{msg} : Are you sure? : [y/n] -> ").lower()

        if selection not in ["y", "n"]:
            print("please make a valid selection.")
        elif selection == "y":
            break
        elif selection == "n":
            exit(0)
        else:
            print("Invalid selection.")
            exit(1)


def expected_cli_args(*expected_args) -> Callable:
    def validate_args_decorator(func: Callable) -> Callable:
        def wrapper(command, *args, **kwargs) -> Any:
            for expected_arg in expected_args:
                if getattr(command.cli_args, expected_arg) is None:
                    print(f"The argument '{expected_arg}' must be provided.")
                    exit(1)
            return func(command, *args, **kwargs)
        return wrapper
    return validate_args_decorator



