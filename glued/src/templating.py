from pathlib import Path
from jinja2 import Template


class TemplateController:

    def __init__(self) -> None:
        self.template_dir = Path(__file__).parent.parent / 'templates'

    def get_template_content(self, template_name: str) -> str:
        return self.template_dir.joinpath(template_name).read_text()
