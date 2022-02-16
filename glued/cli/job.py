import os
import boto3
from argparse import Namespace
from glued.src.project import GluedProject
from glued.src.job import GluedJob
from glued.src.templating import TemplateController


def new(cmd: Namespace) -> None:
    project = GluedProject()
    template_controller = TemplateController()

    # TODO: validate name
    job_name = cmd.name

    glued_job = GluedJob(project.root, job_name)

    config_template = template_controller.get_template_content('job_config.template.yml')
    script_template = template_controller.get_template_content('main.template.py')

    glued_job.create(config_template, script_template)


def sync(cmd: Namespace) -> Namespace:
    print(os.environ)
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
