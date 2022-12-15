import zipfile
from pathlib import Path
from superglue.environment.config import MODULES_PATH
from superglue.core.types import SuperglueModuleType
from superglue.core.components.base import SuperglueComponent
from superglue.environment.variables import SUPERGLUE_S3_BUCKET, SUPERGLUE_IAM_ROLE


class SuperglueModule(SuperglueComponent):

    def __init__(self, module_name: str):

        super(SuperglueModule, self).__init__(
            root_dir=MODULES_PATH,
            component_name=module_name,
            component_type="superglue_module",
            bucket=SUPERGLUE_S3_BUCKET,
            iam_role=SUPERGLUE_IAM_ROLE,

        )

    @property
    def module_name(self) -> str:
        return self.component_name

    @property
    def module_root_path(self) -> Path:
        return self.root_dir / self.module_name

    @property
    def module_inner_path(self) -> Path:
        return self.module_root_path / self.module_name

    @property
    def zipfile(self) -> Path:
        return self.module_root_path / f"{self.module_name}.zip"

    @property
    def s3_zipfile_path(self) -> str:
        relative_path = self.zipfile.relative_to(self.module_root_path)
        return f"{self.s3_path}/{relative_path}"

    @classmethod
    def new(cls, module_name: str) -> SuperglueModuleType:
        return cls(module_name)

    @classmethod
    def get(cls, module_name: str) -> SuperglueModuleType:
        sg_module = cls(module_name)
        if not sg_module.module_root_path.exists():
            raise FileNotFoundError(f"No superglue module {module_name} exists.")
        return sg_module

    def save(self) -> None:
        if not self.module_root_path.exists():
            self.module_inner_path.mkdir(parents=True, exist_ok=True)

            init_py = self.module_inner_path / "__init__.py"
            init_py.touch(exist_ok=True)
            self.save_version_file()
            print(f"created new superglue module {self.module_name}")
        else:
            print(f"shared python module {self.module_name} already exists.")

    def deploy(self) -> None:
        if self.is_deployable:
            self.sync()
            print(f"Superglue module {self.module_name} successfully deployed!")
        elif self.is_edited:
            print(f"Superglue module {self.module_name} has edits in progress. Please run superglue package")
        else:
            print(f"Superglue module {self.module_name} up to date in S3. Nothing to deploy.")

    def delete(self) -> None:
        raise NotImplementedError

    def create_zip(self) -> None:
        with zipfile.ZipFile(self.zipfile, mode="w") as zip_file:
            for file in self.module_root_path.glob("**/*.py"):
                content = file.read_text()
                content = content.encode("utf-8")
                rel_path = file.relative_to(self.module_root_path).as_posix()
                zip_file.writestr(rel_path, content)

    def package(self) -> None:
        if self.is_edited or not self.zipfile.exists():
            self.create_zip()
            self.save_version_file()
            print(f"Superglue module {self.module_name} has been successfully packaged!")
        else:
            print(f"Superglue module {self.module_name} package is up to date!")
