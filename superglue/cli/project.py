from argparse import Namespace
from superglue.core.project import SuperGlueProject
from superglue.helpers.cli import list_modules_to_sync, list_jobs_to_sync, list_stale_modules, list_stale_jobs
from superglue.helpers.cli import validate_account

project = SuperGlueProject()


def init(cmd: Namespace) -> None:
    print("initializing superglue project")
    project.create()


@validate_account
def sync(cmd: Namespace) -> None:
    jobs_to_sync = list_jobs_to_sync(project)

    for job in jobs_to_sync:
        print(f"deploying job {job.job_name}")
        job.deploy()

    modules_to_sync = list_modules_to_sync(project)

    for module in modules_to_sync:
        print(f"deploying module {module.module_name}")
        module.create_zip()
        module.deploy()


@validate_account
def _check_remote() -> None:
    _ = list_jobs_to_sync(project)
    _ = list_modules_to_sync(project)


def status(cmd: Namespace) -> None:
    stale_jobs = [j.job_name for j in list_stale_jobs(project)]
    stale_modules = [m.module_name for m in list_stale_modules(project)]

    if stale_jobs or stale_modules:
        print("The superglue project is not up to date.")

        if stale_jobs:
            print(f"The following jobs need to be committed {stale_jobs}")

        if stale_modules:
            print(f"The following modules need to be committed {stale_modules}")

        exit(1)
    else:
        print("local superglue project is fresh as a daisy!")

    if cmd.remote:
        print("checking remote s3 state")
        _check_remote()


def commit(cmd: Namespace) -> None:

    for stale_job in list_stale_jobs(project):
        stale_job.create_version()

    for stale_module in list_stale_modules(project):
        stale_module.create_version()
