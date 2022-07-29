import boto3
import botocore
from typing import List, Callable, Any
from superglue.core.project import SuperGlueProject
from superglue.core.job import SuperGlueJob
from superglue.core.module import SuperGlueModule
from superglue.environment.variables import SUPERGLUE_AWS_ACCOUNT


def list_jobs_to_sync(project: SuperGlueProject) -> List[SuperGlueJob]:
    jobs_to_sync = []

    for job_name in project.list_jobs():
        job = SuperGlueJob(parent_dir=project.jobs_root, job_name=job_name)

        job.load_config()
        job.create_version()

        local_version = job.version
        remote_version = job.fetch_s3_version()

        if local_version != remote_version:
            print(f"{job.job_name} is not up to date and is marked for deployment")
            jobs_to_sync.append(job)

    return jobs_to_sync


# TODO: These functions probably belong in the project class, not really as helpers.
def list_modules_to_sync(project: SuperGlueProject) -> List[SuperGlueModule]:

    modules_to_sync = []

    for module_name in project.list_modules():
        module = SuperGlueModule(parent_dir=project.shared_root, module_name=module_name)

        module.create_version()
        local_version = module.version

        try:
            remote_version = module.fetch_s3_version()
        except botocore.exceptions.ClientError:
            print("no remote version found")
            remote_version = None

        if local_version != remote_version:
            print(f"{module.module_name} is not up to date and is marked for deployment")
            modules_to_sync.append(module)
    return modules_to_sync


def validate_account(func: Callable) -> Callable:
    def wrapper(*args, **kwargs) -> Any:
        sts = boto3.client("sts")
        account_id = int(sts.get_caller_identity()["Account"])

        if account_id != SUPERGLUE_AWS_ACCOUNT:
            print(f"superglue expects account {SUPERGLUE_AWS_ACCOUNT} but account is {account_id}")
            exit(1)
        return func(*args, **kwargs)
    return wrapper


def list_stale_jobs(project: SuperGlueProject) -> List[SuperGlueJob]:
    stale_jobs = []

    for job_name in project.list_jobs():

        job = SuperGlueJob(parent_dir=project.jobs_root, job_name=job_name)

        job.load_config()

        if job.version != job.get_next_version():
            stale_jobs.append(job)

    return stale_jobs


def list_stale_modules(project: SuperGlueProject) -> List[SuperGlueModule]:

    stale_modules = []

    for module_name in project.list_modules():

        module = SuperGlueModule(parent_dir=project.shared_root, module_name=module_name)

        if module.version != module.get_next_version():
            stale_modules.append(module)

    return stale_modules
