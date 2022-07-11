from argparse import Namespace
from types import SimpleNamespace
from jinja2 import Template
from glued.environment.variables import IAM_ROLE, DEFAULT_S3_BUCKET
from glued.src.project import GluedProject
from glued.src.job import GluedJob
from glued.src.templating import TemplateController
from glued.cli.helpers import validate_input, get_logger


logger = get_logger(__name__)


def new(cmd: Namespace) -> None:
    logger.info(f"creating new glue job config with name {cmd.name}")

    project = GluedProject()
    template_controller = TemplateController()
    job_name = cmd.name

    validate_input(job_name, logger)

    job = GluedJob(project.jobs_root, job_name)

    config_template = template_controller.get_template_content(
        "job_config.template.yml"
    )

    config_template = Template(config_template).render(
        iam_role=IAM_ROLE, script_location=job.s3_script_path
    )

    script_template = template_controller.get_template_content("main.template.py")
    job.create(config_template, script_template)


def deploy(cmd: Namespace) -> None:
    project = GluedProject()
    glued_jobs = project.list_jobs()
    job_name = cmd.name

    validate_input(job_name, logger)

    options = SimpleNamespace()
    options.ALL = 'all'
    options.MODULES = glued_jobs

    match cmd.name:

        case options.ALL:

            for glued_job in glued_jobs:

                job = GluedJob(
                    parent_dir=project.jobs_root, job_name=glued_job, bucket=DEFAULT_S3_BUCKET
                )

                job.load_config()
                job.create_version()
                job.deploy()

        case options.MODULES:

            job = GluedJob(
                parent_dir=project.jobs_root, job_name=cmd, bucket=DEFAULT_S3_BUCKET
            )

            job.load_config()
            job.create_version()
            job.deploy()

        case other:
            logger.error(f'Either provide a valid job name, or the "all" keyword. '
                         f'{cmd.name} not found in glue_jobs directory')


def delete(cmd: Namespace) -> None:

    project = GluedProject()
    job_name = cmd.name
    validate_input(job_name, logger)

    job = GluedJob(
        parent_dir=project.jobs_root, job_name=cmd.name, bucket=DEFAULT_S3_BUCKET
    )

    if not job.job_path.exists():
        print(f"The job {cmd.name} does not exist")
    else:
        job.load_config()
        job.delete()


def check(cmd: Namespace) -> None:
    project = GluedProject()
    job_name = cmd.name
    validate_input(job_name, logger)

    job = GluedJob(
        parent_dir=project.jobs_root, job_name=cmd.name, bucket=DEFAULT_S3_BUCKET
    )

    job.load_config()
    job.dump_config()

