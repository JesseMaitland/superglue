import botocore
from argparse import Namespace
from typing import List
from glued.src.templating import TemplateController
from glued.src.project import GluedProject
from glued.src.job import GluedJob
from glued.src.module import GluedModule
from glued.cli.helpers import get_logger, list_modules_to_sync, list_jobs_to_sync

logger = get_logger(__name__)


def init(cmd: Namespace) -> None:
    logger.info("initializing glued project")
    project = GluedProject()
    template_controller = TemplateController()

    glued_config = template_controller.get_template_content(
        "project_config.template.yml"
    )

    project.create(glued_config)


def sync(cmd: Namespace) -> None:
    project = GluedProject()

    jobs_to_sync = list_jobs_to_sync(project, logger)

    for job in jobs_to_sync:
        logger.info(f"deploying job {job.job_name}")
        job.deploy()

    modules_to_sync = list_modules_to_sync(project, logger)

    for module in modules_to_sync:
        logger.info(f"deploying module {module.module_name}")
        module.create_zip()
        module.deploy()


def status(cmd: Namespace) -> None:

    project = GluedProject()

    _ = list_jobs_to_sync(project, logger)
    _ = list_modules_to_sync(project, logger)

