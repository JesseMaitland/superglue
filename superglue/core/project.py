from pathlib import Path
from typing import List


class SuperGlueProject:
    """ Class represents the superglue project structure """

    def __init__(self) -> None:
        self.jobs_root = Path.cwd() / "glue_jobs"
        self.shared_root = Path.cwd() / "shared"
        self.notebooks = Path.cwd() / "notebooks"
        self.makefile_template = Path(__file__).parent.parent / "templates" / "makefile"

    def create(self) -> None:
        self.jobs_root.mkdir(exist_ok=True)
        self.shared_root.mkdir(exist_ok=True)
        self.notebooks.mkdir(exist_ok=True)

        makefile = Path.cwd() / "makefile"

        if makefile.exists():
            makefile = Path.cwd() / "makefile.sg"

        if not makefile.exists():
            content = self.makefile_template.read_text()
            makefile.touch()
            makefile.write_text(content)

    def list_jobs(self) -> List[str]:
        return [path.name for path in self.jobs_root.iterdir() if path.is_dir()]

    def list_modules(self) -> List[str]:
        return [path.name for path in self.shared_root.iterdir() if path.name != ".DS_Store"]
