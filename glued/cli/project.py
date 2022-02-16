from argparse import Namespace
from glued.src.templating import TemplateController
from glued.src.project import GluedProject


def init(cmd: Namespace) -> None:
    project = GluedProject()
    template_controller = TemplateController()

    glued_config = template_controller.get_template_content('project_config.template.yml')

    project.create(glued_config)

