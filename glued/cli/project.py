from argparse import Namespace
from glued.src.templating import TemplateController
from glued.src.project import GluedProject
from glued.cli.helpers import list_modules_to_sync, list_jobs_to_sync


def init(cmd: Namespace) -> None:
    print("initializing glued project")
    project = GluedProject()
    template_controller = TemplateController()

    glued_config = template_controller.get_template_content("project_config.template.yml")

    project.create(glued_config)


def sync(cmd: Namespace) -> None:
    project = GluedProject()

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
    project = GluedProject()
    _ = list_jobs_to_sync(project)
    _ = list_modules_to_sync(project)
