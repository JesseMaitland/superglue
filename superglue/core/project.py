from pathlib import Path
from typing import List


class SuperGlueProject:
    def __init__(self) -> None:
        self.jobs_root = Path.cwd() / "glue_jobs"
        self.shared_root = Path.cwd() / "shared"

    def create(self) -> None:
        self.jobs_root.mkdir(exist_ok=True)
        self.shared_root.mkdir(exist_ok=True)

    def list_jobs(self) -> List[str]:
        return [path.name for path in self.jobs_root.iterdir() if path.is_dir()]

    def list_modules(self) -> List[str]:
        return [path.name for path in self.shared_root.iterdir() if path.name != ".DS_Store"]
