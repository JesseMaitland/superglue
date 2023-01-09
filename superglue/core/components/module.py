import zipfile
from pathlib import Path
from typing import Optional, TypeVar, List
from superglue.environment.config import MODULES_PATH
from superglue.core.components.base import SuperglueComponent
from superglue.core.components.tests import SuperglueTests
from superglue.environment.variables import SUPERGLUE_S3_BUCKET, SUPERGLUE_IAM_ROLE


SuperglueModuleType = TypeVar("SuperglueModuleType", bound="SuperglueModule")


class SuperglueModule(SuperglueComponent):
    def __init__(
        self,
        name: str,
        version_number: Optional[int] = None,
        tests: Optional[SuperglueTests] = None,
        *args,
        **kwargs,
    ) -> None:

        self.tests = tests or SuperglueTests()

        super(SuperglueModule, self).__init__(
            *args,
            root_dir=MODULES_PATH,
            component_name=name,
            component_type="superglue_module",
            bucket=SUPERGLUE_S3_BUCKET,
            iam_role=SUPERGLUE_IAM_ROLE,
            **kwargs,
        )

        if version_number:
            self.version_number = version_number

    @property
    def module_root_path(self) -> Path:
        return self.root_dir / self.name

    @property
    def module_inner_path(self) -> Path:
        return self.module_root_path / self.name

    @property
    def zipfile(self) -> Path:
        return self.module_root_path / f"{self.name}.zip"

    @property
    def s3_zipfile_path(self) -> str:
        relative_path = self.zipfile.relative_to(self.module_root_path)
        return f"{self.s3_path}/{relative_path}"

    @property
    def module_test_path(self) -> Path:
        return self.tests.modules_test_dir / self.name

    @property
    def module_tests_file(self):
        return self.module_test_path / f"test_{self.name}.py"

    @property
    def is_packaged(self) -> bool:
        return self.zipfile.exists()

    @classmethod
    def new(cls, module_name: str) -> SuperglueModuleType:
        return cls(module_name)

    @classmethod
    def get(cls, module_name: str) -> SuperglueModuleType:
        sg_module = cls(module_name)
        if not sg_module.module_root_path.exists():
            raise FileNotFoundError(f"No superglue module {module_name} exists.")
        return sg_module

    @classmethod
    def from_version(cls, module_name: str, version_number: int) -> SuperglueModuleType:
        sg_module = cls(name=module_name, version_number=version_number)
        if not sg_module.module_root_path.exists():
            raise FileNotFoundError(f"No superglue module {module_name} exists.")
        return sg_module

    def module_files(self) -> List[Path]:
        return list(self.module_root_path.glob("**/*.py"))

    def save(self) -> None:
        self.module_inner_path.mkdir(parents=True, exist_ok=True)
        init_py = self.module_inner_path / "__init__.py"
        init_py.touch(exist_ok=True)
        self.save_version_file()
        self.save_tests()

    def deploy(self) -> None:
        self.sync()

    def delete(self) -> None:
        raise NotImplementedError

    def zipfile_relative_path(self, path: Path) -> str:
        return path.relative_to(self.module_root_path).as_posix()

    def zipfile_content(self, path: Path) -> str:
        return path.read_text(encoding="utf-8")

    def package(self) -> None:
        with zipfile.ZipFile(self.zipfile, mode="w") as zip_file:
            for file in self.module_files():
                content = self.zipfile_content(file)
                relative_path = self.zipfile_relative_path(file)
                zip_file.writestr(relative_path, content)

    def remove_zipfile(self) -> None:
        if self.zipfile.exists():
            self.zipfile.unlink()

    def save_tests(self) -> None:
        jinja = self.get_jinja_environment()
        tests_template = jinja.get_template("module_test.template.py.txt")
        test_content = tests_template.render(module=self.name)

        self.module_test_path.mkdir(exist_ok=True, parents=True)
        self.module_tests_file.touch(exist_ok=True)
        self.module_tests_file.write_text(test_content)
