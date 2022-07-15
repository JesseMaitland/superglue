from pathlib import Path
from typing import List


class GluedProject:
    def __init__(self) -> None:
        self.jobs_root = Path.cwd() / "glue_jobs"
        self.shared_root = Path.cwd() / "shared"

    def create(self, config_template: str) -> None:
        self.jobs_root.mkdir(exist_ok=True)
        self.shared_root.mkdir(exist_ok=True)

        config_path = self.jobs_root / "glued.yml"
        config_path.touch(exist_ok=True)
        config_path.write_text(config_template)

    def list_jobs(self) -> List[str]:
        return [path.name for path in self.jobs_root.iterdir() if path.is_dir()]

    def list_modules(self) -> List[str]:
        return [path.name for path in self.shared_root.iterdir() if path.name != ".DS_Store"]
