from argparse import Namespace
from superglue.core.project import GluedProject
from superglue.core.module import GluedModule


project = GluedProject()


def new(cmd: Namespace) -> None:
    module = GluedModule(parent_dir=project.shared_root, module_name=cmd.name)
    module.create()
    print(f"Created shared glue module at {module.module_path}")


def build(cmd: Namespace) -> None:

    if cmd.name == "all":
        for glued_module in project.list_modules():
            print(f"zipping module {glued_module}")
            module = GluedModule(parent_dir=project.shared_root, module_name=glued_module)
            module.create_version()
            module.create_zip()
        exit()

    if cmd.name in project.list_modules():
        print(f"zipping module {cmd.name}")
        module = GluedModule(parent_dir=project.shared_root, module_name=cmd.name)
        module.create_version()
        module.create_zip()
        exit()

    print(f"Either provide a valid module name, or the 'all' keyword. {cmd.name} not found in glue shared modules")
