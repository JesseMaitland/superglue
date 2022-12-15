from typing import TypeVar
from abc import ABC, abstractmethod
from argparse import Namespace
from superglue.core.project import SuperglueProject


class Command(ABC):

    args = {}
    help = ""

    def __init__(self, cli_args: Namespace) -> None:
        self.cli_args = cli_args
        self.project = SuperglueProject()

    @classmethod
    def method(cls) -> str:
        return cls.__name__.lower()

    @abstractmethod
    def __call__(self) -> None:
        pass


CommandType = TypeVar("CommandType", bound="Command")
