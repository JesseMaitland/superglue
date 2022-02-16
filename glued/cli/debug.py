from argparse import Namespace
from glued.src.project import GluedProject
from glued.src.job import GluedJob

from pathlib import Path


def run(cmd: Namespace) -> None:
    project = GluedProject()
    job = GluedJob(project.root, 'foo')
    job.load_config()
    job.sync_job()
    job.create_or_update_job()
