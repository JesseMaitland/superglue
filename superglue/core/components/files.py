from typing import List
from pathlib import Path
from superglue.core.components.base import SuperglueComponent
from superglue.core.types import SuperglueFilesType


class SuperglueFiles(SuperglueComponent):
    def __init__(self) -> None:
        super(SuperglueFiles, self).__init__(
            root_dir=Path.cwd(), component_type="superglue_files", component_name="files"
        )

    @property
    def gitignore_file(self) -> Path:
        return self.root_dir / ".gitignore"

    @property
    def dotenv_file(self) -> Path:
        return self.root_dir / ".env"

    @property
    def files(self) -> List[Path]:
        return [self.gitignore_file, self.dotenv_file]

    @classmethod
    def new(cls) -> SuperglueFilesType:
        return cls()

    def deploy(self) -> None:
        pass

    def delete(self) -> None:
        pass

    def create_files(self) -> None:
        for file in self.files:
            file.touch(exist_ok=True)

    def write_file_content(self) -> None:
        jinja = self.get_jinja_environment()
        for file in self.files:
            template = jinja.get_template(f"template{file.name}")
            file.write_text(template.render())

    def save(self) -> None:
        self.create_files()
        self.write_file_content()
