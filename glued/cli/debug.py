from argparse import Namespace
from glued.src.project import GluedProject
from glued.src.job import GluedJob
from glued.src.module import GluedModule
from pathlib import Path


def run(cmd: Namespace) -> None:
    project = GluedProject()

    module = GluedModule(
        parent_dir=project.shared_root,
        module_name='spam'
    )

    module.create_zip()
    module.sync()

    job = GluedJob(
        parent_dir=project.jobs_root,
        job_name='foo'
    )

    job.load_config()
    job.deploy()

    print(job.config)

    # module.create_zip()
