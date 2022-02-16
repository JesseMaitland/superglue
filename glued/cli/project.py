from argparse import Namespace
from glued.src.templating import TemplateController
from glued.src.project import GluedProject
from glued.src.job import GluedJob

def init(cmd: Namespace) -> None:
    project = GluedProject()
    template_controller = TemplateController()

    glued_config = template_controller.get_template_content('project_config.template.yml')

    project.create(glued_config)


def sync(cmd: Namespace) -> None:
    project = GluedProject()
    jobs_to_sync = []

    for job_name in project.list_jobs():
        job = GluedJob(
            parent_dir=project.root,
            job_name=job_name
        )

        job.load_config()
        job.create_version()

        local_version = job.version
        remote_version = job.fetch_s3_version()

        if local_version != remote_version:
            print(f"{job.job_name} is not up to date and is marked for deployment.")
            jobs_to_sync.append(job)

    for job in jobs_to_sync:
        job.deploy()

    print("Everything up to date!")
