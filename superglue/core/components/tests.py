from pathlib import Path
from typing import List
from superglue.environment.config import TESTS_PATH
from superglue.core.components.base import SuperglueComponent
from superglue.core.types import SuperglueTestsType


class SuperglueTests(SuperglueComponent):

    def __init__(self) -> None:
        super(SuperglueTests, self).__init__(
            root_dir=TESTS_PATH,
            component_type="superglue_tests",
            component_name="tests"
        )

    @property
    def tests_path(self) -> Path:
        return TESTS_PATH

    @property
    def jobs_test_dir(self) -> Path:
        return self.tests_path / "jobs"

    @property
    def modules_test_dir(self) -> Path:
        return self.tests_path / "modules"

    @property
    def module_init_file(self) -> Path:
        return self.modules_test_dir / "__init__.py"

    @property
    def jobs_init_file(self) -> Path:
        return self.jobs_test_dir / "__init__.py"

    @property
    def test_dirs(self) -> List[Path]:
        return [
            self.tests_path,
            self.jobs_test_dir,
            self.modules_test_dir
        ]

    @classmethod
    def new(cls) -> SuperglueTestsType:
        return cls()

    def deploy(self) -> None:
        pass

    def delete(self) -> None:
        pass

    def save(self) -> None:
        for test_dir in self.test_dirs:
            test_dir.mkdir(exist_ok=True)

        jinja = self.get_jinja_environment()

        module_init_template = jinja.get_template("module_init.template.py")
        module_init_content = module_init_template.render()

        self.module_init_file.touch(exist_ok=True)
        self.module_init_file.write_text(module_init_content)

        jobs_init_template = jinja.get_template("jobs_init.template.py")
        jobs_init_content = jobs_init_template.render()

        self.jobs_init_file.touch(exist_ok=True)
        self.jobs_init_file.write_text(jobs_init_content)
