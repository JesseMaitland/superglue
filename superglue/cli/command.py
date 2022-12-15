from abc import ABC, abstractmethod
from argparse import Namespace
from superglue.core.components.project import SuperglueProject


class SuperglueCommand(ABC):

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
