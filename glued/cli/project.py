from argparse import Namespace
from glued.core.project import GluedProject
from glued.helpers.cli import list_modules_to_sync, list_jobs_to_sync


project = GluedProject()


def init(cmd: Namespace) -> None:
    print("initializing glued project")
    project.create()


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


def status(cmd: Namespace) -> None:
    _ = list_jobs_to_sync(project)
    _ = list_modules_to_sync(project)
