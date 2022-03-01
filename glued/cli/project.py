import botocore
from argparse import Namespace
from glued.src.templating import TemplateController
from glued.src.project import GluedProject
from glued.src.job import GluedJob
from glued.src.module import GluedModule


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
            parent_dir=project.jobs_root,
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

    modules_to_sync = []
    for module_name in project.list_modules():
        module = GluedModule(
            parent_dir=project.shared_root,
            module_name=module_name
        )

        module.create_version()
        module.create_zip()

        local_version = module.version

        try:
            remote_version = module.fetch_s3_version()
        except botocore.exceptions.ClientError:
            print("no remote version found")
            remote_version = None

        if local_version != remote_version:
            modules_to_sync.append(module)

    for module in modules_to_sync:
        print(f'sync module {module.module_name}')
        module.sync()

    print("Everything up to date!")
