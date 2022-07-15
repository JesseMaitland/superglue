from argparse import Namespace
from jinja2 import Template
from glued.environment.variables import IAM_ROLE, DEFAULT_S3_BUCKET
from glued.src.project import GluedProject
from glued.src.job import GluedJob
from glued.src.templating import TemplateController


def new(cmd: Namespace) -> None:
    print(f"creating new glue job config with name {cmd.name}")
    project = GluedProject()
    template_controller = TemplateController()

    job = GluedJob(project.jobs_root, cmd.name)

    config_template = template_controller.get_template_content("job_config.template.yml")

    config_template = Template(config_template).render(iam_role=IAM_ROLE, script_location=job.s3_script_path)

    script_template = template_controller.get_template_content("main.template.py")
    job.create(config_template, script_template)


def deploy(cmd: Namespace) -> None:
    project = GluedProject()

    if cmd.name == "all":
        for glued_job in project.list_jobs():
            job = GluedJob(parent_dir=project.jobs_root, job_name=glued_job, bucket=DEFAULT_S3_BUCKET)

            job.load_config()
            job.create_version()
            job.deploy()
        exit()

    if cmd.name in project.list_jobs():
        job = GluedJob(parent_dir=project.jobs_root, job_name=cmd.name, bucket=DEFAULT_S3_BUCKET)
        job.load_config()
        job.create_version()
        job.deploy()
        exit()

    # in all other cases, there was some kind of invalid argument value
    print(f"Either provide a valid job name, or the 'all' keyword.{cmd.name} not found in glue_jobs directory")


def delete(cmd: Namespace) -> None:
    project = GluedProject()

    job = GluedJob(parent_dir=project.jobs_root, job_name=cmd.name, bucket=DEFAULT_S3_BUCKET)
    job.load_config()
    job.delete()


def check(cmd: Namespace) -> None:
    project = GluedProject()
    job = GluedJob(parent_dir=project.jobs_root, job_name=cmd.name, bucket=DEFAULT_S3_BUCKET)

    job.load_config()
    job.dump_config()
