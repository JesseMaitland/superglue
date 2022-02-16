import os
from argparse import Namespace
from jinja2 import Template
from glued.environment import IAM_ROLE, DEFAULT_S3_BUCKET
from glued.src.project import GluedProject
from glued.src.job import GluedJob
from glued.src.templating import TemplateController


def new(cmd: Namespace) -> None:
    project = GluedProject()
    template_controller = TemplateController()

    # TODO: validate name
    job_name = cmd.name

    job = GluedJob(project.root, job_name)

    config_template = template_controller.get_template_content('job_config.template.yml')
    config_template = Template(config_template).render(iam_role=IAM_ROLE, script_location=job.s3_script_path)

    script_template = template_controller.get_template_content('main.template.py')

    job.create(config_template, script_template)


def deploy(cmd: Namespace) -> Namespace:
    project = GluedProject()
    job = GluedJob(
        parent_dir=project.root,
        job_name=cmd.name,
        bucket=DEFAULT_S3_BUCKET
        )

    if not job.job_path.exists():
        print(f"The job {cmd.name} does not exist")
    else:
        job.load_config()
        job.deploy()


def delete(cmd: Namespace) -> Namespace:
    project = GluedProject()
    job = GluedJob(
        parent_dir=project.root,
        job_name=cmd.name,
        bucket=DEFAULT_S3_BUCKET
    )

    if not job.job_path.exists():
        print(f"The job {cmd.name} does not exist")
    else:
        job.load_config()
        job.delete()
