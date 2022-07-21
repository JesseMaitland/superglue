from argparse import Namespace
from superglue.exceptions import JobNameValidationError
from superglue.environment.variables import SUPERGLUE_IAM_ROLE, SUPERGLUE_S3_BUCKET
from superglue.core.project import SuperGlueProject
from superglue.core.job import SuperGlueJob
from superglue.helpers.cli import validate_account


project = SuperGlueProject()


def new(cmd: Namespace) -> None:
    """
    Creates a new job in the glue_jobs directory
    """
    job = SuperGlueJob(project.jobs_root, cmd.name)

    try:
        job.validate_name()
    except JobNameValidationError as e:
        print(e.args[0])
        exit()

    job.create(
        iam_role=SUPERGLUE_IAM_ROLE,
        job_name=cmd.name,
        script_location=job.s3_script_path
    )

    print(f"created new glue job config with name {cmd.name}")


@validate_account
def deploy(cmd: Namespace) -> None:
    if cmd.name == "all":
        for glued_job in project.list_jobs():
            job = SuperGlueJob(parent_dir=project.jobs_root, job_name=glued_job, bucket=SUPERGLUE_S3_BUCKET)

            job.load_config()
            job.create_version()
            job.deploy()
        exit()

    if cmd.name in project.list_jobs():
        job = SuperGlueJob(parent_dir=project.jobs_root, job_name=cmd.name, bucket=SUPERGLUE_S3_BUCKET)
        job.load_config()
        job.create_version()
        job.deploy()
        exit()

    # in all other cases, there was some kind of invalid argument value
    print(f"Either provide a valid job name, or the 'all' keyword.{cmd.name} not found in glue_jobs directory")


@validate_account
def delete(cmd: Namespace) -> None:
    job = SuperGlueJob(parent_dir=project.jobs_root, job_name=cmd.name, bucket=SUPERGLUE_S3_BUCKET)
    job.load_config()
    job.delete()


@validate_account
def check(cmd: Namespace) -> None:
    job = SuperGlueJob(parent_dir=project.jobs_root, job_name=cmd.name, bucket=SUPERGLUE_S3_BUCKET)
    job.load_config()
    job.dump_config()
