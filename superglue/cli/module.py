from argparse import Namespace
from superglue.core.project import SuperGlueProject, SuperGlueModule
from superglue.helpers.cli import yes_no_confirmation

project = SuperGlueProject()


def new(cmd: Namespace) -> None:
    module = SuperGlueModule(parent_dir=project.shared_root, module_name=cmd.name)
    module.create()
    print(f"Created shared glue module at {module.module_path}")


def build(cmd: Namespace) -> None:

    superglue_module = SuperGlueModule(parent_dir=project.shared_root, module_name=cmd.name)
    yes_no_confirmation(
        f"This will build a zip archive for the shared superglue module {superglue_module.module_name}."
    )

    print(f"zipping module {cmd.name}")
    superglue_module.create_version()
    superglue_module.create_zip()
    print("success")
    exit(0)


def deploy(cmd: Namespace) -> None:

    superglue_module = SuperGlueModule(parent_dir=project.shared_root, module_name=cmd.name)
    yes_no_confirmation(
        f"This will build and deploy a zip archive for the shared superglue module {superglue_module.module_name}."
    )

    print(f"zipping and deploying module {superglue_module.module_name}")
    superglue_module.create_version()
    superglue_module.create_zip()
    superglue_module.deploy()
    print("success")
    exit(0)
