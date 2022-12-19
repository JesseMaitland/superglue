import boto3
import inspect
from typing import List, Any, Callable
from types import ModuleType
from superglue.cli.command import SuperglueCommand
from superglue.core.types import SuperglueCommandType
from superglue.environment.variables import SUPERGLUE_AWS_ACCOUNT


def get_commands(module: ModuleType) -> List[SuperglueCommandType]:
    commands = []
    for _, _class in inspect.getmembers(module, inspect.isclass):
        if _class != SuperglueCommand:
            if issubclass(_class, SuperglueCommand):
                commands.append(_class)
    return commands


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


def get_parser_name(name: str) -> str:
    return name.split(".")[-1]


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
