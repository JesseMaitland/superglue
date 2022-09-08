from argparse import ArgumentParser, Action, Namespace
from typing import Any
from superglue.core.project import SuperGlueProject, SuperGlueJob, SuperGlueModule


def validate_input_string(input_string: str, message: str) -> None:
    forbidden = "!" "#$%&'()*+,./:;<=>?@[\\]^`{|}~"
    for char in input_string:
        if char in forbidden:
            print(message)
            exit()


def check_job_exists(job_name: str) -> None:

    project = SuperGlueProject()
    job = SuperGlueJob(project.jobs_root, job_name)

    if not job.job_path.exists():
        print(f"The job {job.job_name} does not exist")
        exit()


def check_module_exists(module_name: str) -> None:

    project = SuperGlueProject()
    module = SuperGlueModule(project.shared_root, module_name)

    if not module.module_path.exists():
        print(f"The module {module.module_name} does not exist")
        exit()


class ValidateJobCommandName(Action):
    def __call__(self, parser: ArgumentParser, namespace: Namespace, values: Any, option_string: str = None):
        validate_input_string(values, f"The {values} is not allowed in job names")

        # The job of course cannot already exist if we ar calling the new cmd
        if not namespace.func.__name__ == "new":
            check_job_exists(values)

        setattr(namespace, self.dest, values)


class ValidateModuleCommandName(Action):
    def __call__(self, parser: ArgumentParser, namespace: Namespace, values: Any, option_string: str = None):

        validate_input_string(values, f"The {values} is not allowed in job names")

        # The module of course cannot already exist if we ar calling the new cmd
        if not namespace.func.__name__ == "new":
            check_module_exists(values)

        setattr(namespace, self.dest, values)
