from superglue.cli.utils import validate_account
from superglue.cli.command import SuperglueCommand


__version__ = "0.3.2"


class Version(SuperglueCommand):

    args = {}
    help = "--> Print the current version of superglue and exit."

    def __call__(self) -> None:
        print(f"The AWS Glue Deployment Utility -- superglue version :: {__version__}")


class Account(SuperglueCommand):

    help = "--> Print the AWS account number that superglue is configured to use."

    @validate_account
    def __call__(self) -> None:
        pass


class Init(SuperglueCommand):

    help = "--> Creates a new superglue project structure."

    def __call__(self) -> None:
        self.project.create()
        print("superglue project initialized!")


class Package(SuperglueCommand):

    help = "--> Packages all superglue jobs and modules which have been edited since the last package was issued."

    def __call__(self) -> None:
        edited = self.project.modules.edited()
        if edited:
            for module in edited:
                module.package()
        else:
            print("No changes in superglue modules found. Nothing to package.")

        edited = self.project.jobs.edited()

        if edited:
            for job in edited:
                job.package()
        else:
            print("No changes in superglue jobs found. Nothing to package.")


class Status(SuperglueCommand):

    help = "--> Prints the current status of all superglue jobs and modules."

    @validate_account
    def __call__(self) -> None:
        table = self.project.get_pretty_table()

        for module in self.project.modules:
            table.add_row(module.pretty_table_row)

        for job in self.project.jobs:
            table.add_row(job.pretty_table_row)

        print(table)


class Deploy(SuperglueCommand):

    help = "--> Deploys all superglue jobs and modules which have been changed since the last issued deployment."

    args = {("-p", "--package"): {"action": "store_true", "default": False}}

    def __call__(self) -> None:
        if self.cli_args.package:
            print("Packaging before deployment")
            for module in self.project.modules.edited():
                module.package()

            for job in self.project.jobs.edited():
                job.package()
        else:
            if self.project.modules.edited() or self.project.jobs.edited():
                print("Active edits in progress. Please run superglue package before attempting deployment")
                exit(1)

        deployable_modules = self.project.modules.deployable()
        if deployable_modules:
            for module in deployable_modules:
                module.deploy()
        else:
            print("All superglue modules are up to date in S3. Nothing to deploy.")

        deployable_jobs = self.project.jobs.deployable()

        if deployable_jobs:
            for job in deployable_jobs:
                job.deploy()
        else:
            print("All superglue jobs are up to date in S3. Nothing to deploy.")


class Generate(SuperglueCommand):

    help = "--> Used to generate superglue tests, and utility files"

    args = {
        ("-t", "--tests"): {"action": "store_true", "default": False},
        ("-m", "--makefile"): {"action": "store_true", "default": False},
    }

    def __call__(self) -> None:

        if self.cli_args.tests:
            for job in self.project.jobs:
                job.save_tests()

            for module in self.project.modules:
                module.save_tests()

        if self.cli_args.makefile:
            makefile = self.project.makefile.new()
            makefile.save()
