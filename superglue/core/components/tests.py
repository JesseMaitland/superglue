from pathlib import Path
from typing import List
from superglue.environment.config import TESTS_PATH
from superglue.core.components.base import SuperglueComponent
from superglue.core.types import SuperglueTestsType


class SuperglueTests(SuperglueComponent):
    def __init__(self) -> None:
        super(SuperglueTests, self).__init__(
            root_dir=TESTS_PATH, component_type="superglue_tests", component_name="tests"
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
    def conftest_file(self) -> Path:
        return self.tests_path / "conftest.py"

    @property
    def test_dirs(self) -> List[Path]:
        return [self.tests_path, self.jobs_test_dir, self.modules_test_dir]

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

        conftest_template = jinja.get_template("conftest.template.py")

        self.conftest_file.touch(exist_ok=True)
        self.conftest_file.write_text(conftest_template.render())
