from argparse import Namespace
from glued.src.project import GluedProject
from glued.src.job import GluedJob

from pathlib import Path

def run(cmd: Namespace) -> None:
    project = GluedProject()
    job = GluedJob(project.root, 'foo')
    job.create_version()
    remote_version = job.fetch_s3_version()
    print(remote_version)
    print(remote_version == job.version)
