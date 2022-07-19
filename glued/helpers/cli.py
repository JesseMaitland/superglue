import botocore
from typing import List
from glued.core.project import GluedProject
from glued.core.job import GluedJob
from glued.core.module import GluedModule


def list_jobs_to_sync(project: GluedProject) -> List[GluedJob]:
    jobs_to_sync = []

    for job_name in project.list_jobs():
        job = GluedJob(parent_dir=project.jobs_root, job_name=job_name)

        job.load_config()
        job.create_version()

        local_version = job.version
        remote_version = job.fetch_s3_version()

        if local_version != remote_version:
            print(f"{job.job_name} is not up to date and is marked for deployment")
            jobs_to_sync.append(job)

    return jobs_to_sync


def list_modules_to_sync(project: GluedProject) -> List[GluedModule]:

    modules_to_sync = []

    for module_name in project.list_modules():
        module = GluedModule(parent_dir=project.shared_root, module_name=module_name)

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
