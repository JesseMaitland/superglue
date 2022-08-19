from argparse import Namespace
from superglue.core.project import SuperGlueProject, SuperGlueModule


project = SuperGlueProject()


def new(cmd: Namespace) -> None:
    module = SuperGlueModule(parent_dir=project.shared_root, module_name=cmd.name)
    module.create()
    print(f"Created shared glue module at {module.module_path}")


def build(cmd: Namespace) -> None:

    if cmd.name == "all":
        for superglue_module in project.list_modules():
            print(f"zipping module {superglue_module.module_name}")
            superglue_module.create_version()
            superglue_module.create_zip()
        exit()

    else:
        superglue_module = SuperGlueModule(parent_dir=project.shared_root, module_name=cmd.name)

        if not superglue_module.module_path.exists():
            print(f"Either provide a valid module name, or the 'all' keyword. {cmd.name} not found in glue shared modules")
            exit()

        print(f"zipping module {cmd.name}")
        superglue_module.create_version()
        superglue_module.create_zip()
        exit()


