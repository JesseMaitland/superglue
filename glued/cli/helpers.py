import botocore
from logging import Logger
from typing import List
from glued.environment.variables import GLUED_LOGGER_DIR
from glued.src.logger_factory import format_logger_filename, logger_factory
from glued.src.project import GluedProject
from glued.src.job import GluedJob
from glued.src.module import GluedModule


def get_logger(name: str):
    logger_file = format_logger_filename()
    logger = logger_factory(file_path=GLUED_LOGGER_DIR.joinpath(logger_file), logger_name=name)
    return logger


def validate_input(name: str, logger: Logger) -> str:
    forbidden = "!""#$%&\'()*+,./:;<=>?@[\\]^`{|}~"

    for char in name:
        if char in forbidden:
            logger.error(f"The character {char} is not allowed in job names. ")
            exit()


def list_jobs_to_sync(project: GluedProject, logger: Logger) -> List[GluedJob]:
    jobs_to_sync = []

    for job_name in project.list_jobs():
        job = GluedJob(parent_dir=project.jobs_root, job_name=job_name)

        job.load_config()
        job.create_version()

        local_version = job.version
        remote_version = job.fetch_s3_version()

        if local_version != remote_version:
            logger.info(f"{job.job_name} is not up to date and is marked for deployment")
            jobs_to_sync.append(job)

    return jobs_to_sync


def list_modules_to_sync(project: GluedProject, logger: Logger) -> List[GluedModule]:
    modules_to_sync = []
    for module_name in project.list_modules():
        module = GluedModule(parent_dir=project.shared_root, module_name=module_name)

        module.create_version()
        local_version = module.version

        try:
            remote_version = module.fetch_s3_version()
        except botocore.exceptions.ClientError:
            print("no remote version found")
            remote_version = None

        if local_version != remote_version:
            logger.info(f"{module.module_name} is not up to date and is marked for deployment")
            modules_to_sync.append(module)
    return modules_to_sync
