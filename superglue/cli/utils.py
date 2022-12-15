import boto3
import inspect
from typing import List, Type, Any, Callable
from types import ModuleType
from superglue.cli.command import CommandType, Command
from superglue.environment.variables import SUPERGLUE_AWS_ACCOUNT


def get_commands(module: ModuleType) -> List[Type[CommandType]]:
    commands = []
    for _, _class in inspect.getmembers(module, inspect.isclass):
        if _class != Command:
            if issubclass(_class, Command):
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
    return name.split('.')[-1]
