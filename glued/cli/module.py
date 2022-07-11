from argparse import Namespace
from types import SimpleNamespace
from glued.src.project import GluedProject
from glued.src.module import GluedModule
from glued.cli.helpers import get_logger

logger = get_logger(__name__)


def new(cmd: Namespace) -> None:
    logger.info(f"Creating new shared glue module called {cmd.name}")

    project = GluedProject()
    module = GluedModule(parent_dir=project.shared_root, module_name=cmd.name)
    module.create()

    logger.info(f"Created shared glue module at {module.module_path}")


def build(cmd: Namespace) -> None:
    project = GluedProject()
    glued_modules = project.list_modules()

    options = SimpleNamespace()
    options.ALL = 'all'
    options.MODULES = glued_modules

    match cmd.name:

        case options.ALL:
            logger.info('zipping all modules')
            for glued_module in glued_modules:
                logger.info(f"zipping module {glued_module}")
                module = GluedModule(parent_dir=project.shared_root, module_name=glued_module)
                module.create_version()
                module.create_zip()

        case options.MODULES:
            logger.info(f'zipping module {cmd.name}')
            module = GluedModule(parent_dir=project.shared_root, module_name=cmd.name)
            module.create_version()
            module.create_zip()

        case other:
            logger.error(f'Either provide a valid module name, or the "all" keyword. '
                         f'{cmd.name} not found in glue shared modules')
