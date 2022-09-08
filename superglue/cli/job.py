from argparse import Namespace
from superglue.exceptions import JobNameValidationError
from superglue.environment.variables import SUPERGLUE_IAM_ROLE, SUPERGLUE_S3_BUCKET, SUPERGLUE_AWS_ACCOUNT
from superglue.core.project import SuperGlueProject, SuperGlueJob
from superglue.helpers.cli import validate_account, yes_no_confirmation


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
        exit(1)

    job.create(
        iam_role=SUPERGLUE_IAM_ROLE, job_name=cmd.name, script_location=job.s3_script_path, override=cmd.override
    )
    print(f"created new glue job {cmd.name}")
    exit(0)


@validate_account
def deploy(cmd: Namespace) -> None:

    if cmd.name in project.list_job_names():
        job = SuperGlueJob(parent_dir=project.jobs_root, job_name=cmd.name, bucket=SUPERGLUE_S3_BUCKET)
        yes_no_confirmation(f"This will deploy the job {job.job_name} to account {SUPERGLUE_AWS_ACCOUNT}.")

        job.load_config()
        job.create_version()
        job.deploy()
        exit(0)
    else:
        print(f"Provide a valid job name for deployment. {cmd.name} not found in glue_jobs directory")
        exit(1)


@validate_account
def delete(cmd: Namespace) -> None:
    job = SuperGlueJob(parent_dir=project.jobs_root, job_name=cmd.name, bucket=SUPERGLUE_S3_BUCKET)

    yes_no_confirmation(f"This will delete the job {job.job_name}.")
    job.load_config()
    job.delete()


def check(cmd: Namespace) -> None:
    job = SuperGlueJob(parent_dir=project.jobs_root, job_name=cmd.name, bucket=SUPERGLUE_S3_BUCKET)
    job.load_config()

    if job.overrides:
        for overridden_job in job.instantiate_overridden_jobs():
            overridden_job.dump_config()
    else:
        job.dump_config()
