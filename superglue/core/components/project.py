import operator
from pathlib import Path
from typing import List, Type
from prettytable import PrettyTable
from superglue.environment.config import JOBS_PATH, MODULES_PATH, NOTEBOOKS_PATH, TOOLS_PATH
from superglue.core.components.component_list import SuperglueComponentList
from superglue.core.components.makefile import SuperglueMakefile
from superglue.core.components.module import SuperglueModule
from superglue.core.components.job import SuperglueJob
from superglue.core.components.tests import SuperglueTests
from superglue.core.components.files import SuperglueFiles


class SuperglueProject:
    """Class represents the superglue project structure"""

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
    def tools_path(self) -> Path:
        return TOOLS_PATH

    @property
    def project_dirs(self) -> List[Path]:
        return [self.jobs_path, self.modules_path, self.notebooks_path, self.tools_path]

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
    def makefile(self) -> Type[SuperglueMakefile]:
        return SuperglueMakefile

    @property
    def tests(self) -> Type[SuperglueTests]:
        return SuperglueTests

    @property
    def files(self) -> Type[SuperglueFiles]:
        return SuperglueFiles

    @property
    def pretty_table_fields(self) -> List[str]:
        return ["Component Name", "Component Type", "Local Stats", "s3 Status", "Version Number"]

    def is_locked(self) -> bool:
        return self.jobs.are_locked() and self.modules.are_locked()

    def save_project_component(self, component_name: str) -> None:
        component_property = getattr(self, component_name)
        component = component_property.new()
        component.save()

    def save_base_project(self) -> None:
        for project_dir in self.project_dirs:
            project_dir.mkdir(exist_ok=True)

    def save_project_components(self) -> None:
        for component in "makefile", "files", "tests":
            self.save_project_component(component)

    def create(self) -> None:
        self.save_base_project()
        self.save_project_components()

    def get_pretty_table(self) -> PrettyTable:
        table = PrettyTable()
        table.field_names = self.pretty_table_fields
        table.sort_key = operator.itemgetter(0, 1)
        table.sortby = "Component Type"
        for field in self.pretty_table_fields:
            if field != "Version Number":
                table.align[field] = "l"
        return table
