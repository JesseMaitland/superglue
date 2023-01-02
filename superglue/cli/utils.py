import boto3
import inspect
from types import ModuleType
from typing import List, Any, Callable, Type
from superglue.cli.base import BaseSuperglueCommand
from superglue.environment.variables import SUPERGLUE_AWS_ACCOUNT


def get_commands(module: ModuleType) -> List[Type[BaseSuperglueCommand]]:
    commands = []
    for _, _class in inspect.getmembers(module, inspect.isclass):
        if _class != BaseSuperglueCommand:
            if issubclass(_class, BaseSuperglueCommand):
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
