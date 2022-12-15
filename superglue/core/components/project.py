import operator
from pathlib import Path
from typing import List, Type
from prettytable import PrettyTable
from superglue.environment.config import JOBS_PATH, MODULES_PATH, NOTEBOOKS_PATH
from superglue.core.components.component_list import SuperglueComponentList
from superglue.core.components.module import SuperglueModule
from superglue.core.components.job import SuperglueJob


class SuperglueProject:
    """Class represents the superglue project structure"""

    def __init__(self) -> None:
        self.makefile_template = Path(__file__).parent.parent / "templates" / "makefile"

    @property
    def jobs_path(self) -> Path:
        return JOBS_PATH

    @property
    def modules_path(self) -> Path:
        return MODULES_PATH

    @property
    def notebooks_path(self) -> Path:
        return NOTEBOOKS_PATH

    @property
    def job(self) -> Type[SuperglueJob]:
        return SuperglueJob

    @property
    def jobs(self) -> SuperglueComponentList[SuperglueJob]:
        jobs = [self.job.get(p.name) for p in self.jobs_path.iterdir()]
        return SuperglueComponentList(jobs)

    @property
    def module(self) -> Type[SuperglueModule]:
        return SuperglueModule

    @property
    def modules(self) -> SuperglueComponentList[SuperglueModule]:
        modules = [self.module.get(p.name) for p in self.modules_path.iterdir()]
        return SuperglueComponentList(modules)

    @property
    def pretty_table_fields(self) -> List[str]:
        return ["Component Name", "Component Type", "Local Stats", "s3 Status", "Version Number"]

    def create(self) -> None:
        self.jobs_path.mkdir(exist_ok=True)
        self.modules_path.mkdir(exist_ok=True)
        self.notebooks_path.mkdir(exist_ok=True)

        makefile = Path.cwd() / "makefile"

        if makefile.exists():
            makefile = Path.cwd() / "makefile.sg"

        if not makefile.exists():
            content = self.makefile_template.read_text()
            makefile.touch()
            makefile.write_text(content)

    def included_modules(self, job: SuperglueJob) -> SuperglueComponentList:
        modules = [self.module.get(name) for name in job.superglue_modules]
        return SuperglueComponentList(modules)

    def get_pretty_table(self) -> PrettyTable:
        table = PrettyTable()
        table.field_names = self.pretty_table_fields
        table.sort_key = operator.itemgetter(0, 1)
        table.sortby = "Component Type"
        for field in self.pretty_table_fields:
            if field != "Version Number":
                table.align[field] = "l"
        return table
