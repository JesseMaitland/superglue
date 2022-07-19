from argparse import Namespace
from jinja2 import Template
from glued.exceptions import JobNameValidationError
from glued.environment.variables import GLUED_IAM_ROLE, GLUED_S3_BUCKET
from glued.core.project import GluedProject
from glued.core.job import GluedJob
from glued.core.templating import TemplateController

project = GluedProject()


def new(cmd: Namespace) -> None:
    template_controller = TemplateController()
    job = GluedJob(project.jobs_root, cmd.name)

    try:
        job.validate_name()
    except JobNameValidationError as e:
        print(e.args[0])
        exit()

    config_template = template_controller.get_template_content("job_config.template.yml")

    config_template = Template(config_template).render(
        iam_role=GLUED_IAM_ROLE,
        job_name=cmd.name,
        script_location=job.s3_script_path)

    script_template = template_controller.get_template_content("main.template.py")
    job.create(config_template, script_template)

    print(f"created new glue job config with name {cmd.name}")


def deploy(cmd: Namespace) -> None:
    if cmd.name == "all":
        for glued_job in project.list_jobs():
            job = GluedJob(parent_dir=project.jobs_root, job_name=glued_job, bucket=GLUED_S3_BUCKET)

            job.load_config()
            job.create_version()
            job.deploy()
        exit()

    if cmd.name in project.list_jobs():
        job = GluedJob(parent_dir=project.jobs_root, job_name=cmd.name, bucket=GLUED_S3_BUCKET)
        job.load_config()
        job.create_version()
        job.deploy()
        exit()

    # in all other cases, there was some kind of invalid argument value
    print(f"Either provide a valid job name, or the 'all' keyword.{cmd.name} not found in glue_jobs directory")


def delete(cmd: Namespace) -> None:
    job = GluedJob(parent_dir=project.jobs_root, job_name=cmd.name, bucket=GLUED_S3_BUCKET)
    job.load_config()
    job.delete()


def check(cmd: Namespace) -> None:
    job = GluedJob(parent_dir=project.jobs_root, job_name=cmd.name, bucket=GLUED_S3_BUCKET)
    job.load_config()
    job.dump_config()
