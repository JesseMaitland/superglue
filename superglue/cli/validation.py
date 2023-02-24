from argparse import ArgumentParser, Action, Namespace
from typing import Any, List
from superglue.core.components.project import SuperglueProject


def get_forbidden_chars(input_string: str) -> List[str]:
    forbidden = "!" "#$%&'()*+,./:;<=>?@[\\]^`{|}~-"
    captured = []
    for char in input_string:
        if char in forbidden:
            captured.append(char)
    return captured


def exit_if_job_exists(job_name: str) -> None:

    project = SuperglueProject()
    job = project.job.new(job_name)

    if job.job_path.exists():
        print(f"The job {job.job_name} already exists")
        exit(1)


#
#
# def check_module_exists(module_name: str) -> None:
#
#     project = SuperGlueProject()
#     module = SuperGlueModule(project.shared_path, module_name)
#
#     if not module.module_path.exists():
#         print(f"The module {module.module_name} does not exist")
#         exit()
#
#
class ValidateNameArgument(Action):
    def __call__(self, parser: ArgumentParser, namespace: Namespace, values: Any, option_string: str = None):
        forbidden_chars = get_forbidden_chars(values)

        if forbidden_chars:
            print(f"The {forbidden_chars} characters are not allowed in superglue component names")
            exit(1)

        setattr(namespace, self.dest, values)


#
#
# class ValidateModuleCommandName(Action):
#     def __call__(self, parser: ArgumentParser, namespace: Namespace, values: Any, option_string: str = None):
#
#         validate_input_string(values, f"The {values} is not allowed in job names")
#
#         # The module of course cannot already exist if we ar calling the new cmd
#         if not namespace.func.__name__ == "new":
#             check_module_exists(values)
#
#         setattr(namespace, self.dest, values)
