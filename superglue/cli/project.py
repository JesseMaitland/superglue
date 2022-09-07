from argparse import Namespace
from superglue.core.project import SuperGlueProject
from superglue.helpers.cli import validate_account

project = SuperGlueProject()


def init(cmd: Namespace) -> None:
    print("initializing superglue project")
    project.create()


@validate_account
def deploy(cmd: Namespace) -> None:
    jobs_to_sync = project.list_jobs_to_sync()

    for job in jobs_to_sync:
        print(f"deploying job {job.job_name}")
        job.deploy()

    modules_to_sync = project.list_modules_to_sync()

    for module in modules_to_sync:
        print(f"deploying module {module.module_name}")
        module.create_zip()
        module.deploy()


@validate_account
def _check_remote() -> None:
    _ = project.list_jobs_to_sync()
    _ = project.list_modules_to_sync()


def status(cmd: Namespace) -> None:

    if cmd.remote:
        print("checking remote s3 state")
        _check_remote()
        exit(0)

    stale_jobs = [j.job_name for j in project.list_stale_jobs()]
    stale_modules = [m.module_name for m in project.list_stale_modules()]

    if stale_jobs or stale_modules:
        print("The superglue project is not up to date.")

        if stale_jobs:
            print(f"The following jobs need to be committed {stale_jobs}")

        if stale_modules:
            print(f"The following modules need to be committed {stale_modules}")

        exit(1)
    else:
        print("local superglue project is fresh as a daisy!")


def commit(cmd: Namespace) -> None:

    for stale_job in project.list_stale_jobs():
        stale_job.create_version()

    for stale_module in project.list_stale_modules():
        stale_module.create_version()
