from argparse import Namespace
from glued.src.project import GluedProject
from glued.src.module import GluedModule


def new(cmd: Namespace) -> None:
    project = GluedProject()

    module = GluedModule(parent_dir=project.shared_root, module_name=cmd.name)

    module.create()
