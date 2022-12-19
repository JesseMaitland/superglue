from pathlib import Path
from superglue.environment.config import TOOLS_PATH
from superglue.core.components.base import SuperglueComponent
from superglue.core.types import SuperglueMakefileType


class SuperglueMakefile(SuperglueComponent):
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

    def deploy(self) -> None:
        pass

    def delete(self) -> None:
        pass

    def save(self) -> None:
        if not self.makefile_path.exists():
            jinja = self.get_jinja_environment()

            makefile_template = jinja.get_template("makefile")
            makefile_content = makefile_template.render()

            self.makefile_path.touch(exist_ok=True)
            self.makefile_path.write_text(makefile_content)

            self.root_makefile.touch(exist_ok=True)
            self.root_makefile.write_text("include tools/makefile")
        else:
            print("Superglue makefile already exists in tools/makefile.")
            print("Manually delete it and rerun this command to get a fresh one.")
