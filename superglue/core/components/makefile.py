from pathlib import Path
from typing import TypeVar
from superglue.environment.config import TOOLS_PATH
from superglue.core.components.base import BaseSuperglueComponent


SuperglueMakefileType = TypeVar("SuperglueMakefileType", bound="SuperglueMakefile")


class SuperglueMakefile(BaseSuperglueComponent):
    def __init__(self) -> None:
        super(SuperglueMakefile, self).__init__(
            root_dir=TOOLS_PATH, component_type="superglue_tool", component_name="makefile"
        )

    @property
    def root_makefile(self) -> Path:
        return Path.cwd() / "makefile"

    @property
    def makefile_path(self) -> Path:
        return TOOLS_PATH / "makefile"

    @classmethod
    def new(cls) -> SuperglueMakefileType:
        return cls()

    def save_root_makefile(self) -> None:
        self.root_makefile.touch(exist_ok=True)
        self.root_makefile.write_text("include tools/makefile")

    def save_tools_makefile(self, content: str) -> None:
        self.makefile_path.touch(exist_ok=True)
        self.makefile_path.write_text(content)

    def get_tools_makefile_content(self) -> str:
        jinja = self.get_jinja_environment()
        return jinja.get_template("makefile").render()

    def save(self) -> None:
        if not self.makefile_path.exists():
            content = self.get_tools_makefile_content()
            self.save_tools_makefile(content)
            self.save_root_makefile()
        else:
            print("Superglue makefile already exists in tools/makefile.")
            print("Manually delete it and rerun this command to get a fresh one.")
