from pathlib import Path
from typing import List


class GluedProject:

    def __init__(self) -> None:
        self.root = Path.cwd() / 'glue_jobs'

    def create(self, config_template: str) -> None:
        self.root.mkdir(exist_ok=True)

        config_path = self.root / 'glued.yml'
        config_path.touch(exist_ok=True)
        config_path.write_text(config_template)

    def list_jobs(self) -> List[str]:
        return [path.name for path in self.root.iterdir()]
