from superglue.cli.command import SuperglueCommand
from superglue.cli.utils import validate_account, get_parser_name


parser_name = get_parser_name(__name__)
cli_help = "--> Interact with superglue jobs"


class BaseArgs:

    args = {("-n", "--name"): {"required": True, "help": "Name of the superglue job (directory)"}}


class New(BaseArgs, SuperglueCommand):

    help = "--> Create a new superglue job directory."

    def __call__(self):
        job = self.project.job.new(self.cli_args.name)
        job.save()


class Status(SuperglueCommand):

    help = "--> Print the current status of all superglue jobs"

    @validate_account
    def __call__(self):
        table = self.project.get_pretty_table()

        for job in self.project.jobs:
            table.add_row(job.pretty_table_row)

        print(table)


class Package(SuperglueCommand):

    help = "--> Packages superglue jobs and dependent modules which have changed since the last issued package command"

    def __call__(self) -> None:

        if self.project.jobs.edited():
            for job in self.project.jobs.edited():
                for module in job.modules():
                    module.package()
                job.package()
        else:
            print("No changes found to superglue jobs. Nothing to package. All jobs are up to date.")


class Build(BaseArgs, SuperglueCommand):

    help = "--> Create or overwrite the 'deployment.yml' file for a given job."

    def __call__(self) -> None:
        job = self.project.job.get(self.cli_args.name)
        job.render()
        job.save_deployment_config()


class Deploy(BaseArgs, SuperglueCommand):

    help = "--> Manually deploy a superglue job. Jobs must first be up to date using the package command."

    def __call__(self) -> None:
        job = self.project.job.get(self.cli_args.name)

        for module in job.modules():
            module.package()
            module.deploy()

        job.deploy()
