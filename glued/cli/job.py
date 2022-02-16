import os
import boto3
from argparse import Namespace
from jinja2 import Template
from glued.environment import IAM_ROLE
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


def sync(cmd: Namespace) -> Namespace:
    project = GluedProject()
    bucket = os.getenv('S3_BUCKET')
    glue_client = boto3.client('glue')
    s3_client = boto3.client('s3')

    glued_job = GluedJob(parent_dir=project.root,
                         job_name=cmd.name,
                         bucket=bucket,
                         glue_client=None,
                         s3_client=None)

    glued_job.sync_job()
