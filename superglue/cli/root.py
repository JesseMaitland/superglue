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

    args = {("-d", "--delete"): {"action": "store_true", "default": False}}

    def __call__(self) -> None:

        if self.cli_args.delete:
            for module in self.project.modules:
                if module.zipfile.exists():
                    module.zipfile.unlink()
                    print(f"Removed package for superglue module {module.module_name}")
            exit(0)

        if not self.project.modules.are_locked():
            print("Not all superglue modules are locked. Please lock them with the superglue lock command.")
            exit(1)

        for module in self.project.modules.locked():
            module.package()
            print(f"Packaging Superglue Module :: {module.module_name}")



class Lock(SuperglueCommand):

    help = "--> Lock superglue jobs and modules to the next version if they have active edits."

    def __call__(self) -> None:

        print("\n------------------> Locking Superglue Jobs <------------------\n")

        for job in self.project.jobs.unlocked():
            print(f"Locking Job -----> {job.job_name} :: Version {job.next_version_number}")
            job.lock()

        print("\n------------------> Locking Superglue Modules <------------------\n")

        for module in self.project.modules.unlocked():
            print(f"Locking Module -----> {module.module_name}")
            module.lock()



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
        ("-d", "--deployment"): {"action": "store_true", "default": False},
        ("-j", "--job"): {"required": False}
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

        if self.cli_args.deployment and not self.cli_args.job:
            print("The --job must be specified when calling generate --deployment")
            exit(1)

        if self.cli_args.deployment:
            job = self.project.job.get(self.cli_args.job)
            job.generate_deployment_yml()


class Check(SuperglueCommand):

    help = "--> Used to check the status of the superglue project before a deployment"

    @validate_account
    def __call__(self) -> None:

        is_deployable = True

        for job in self.project.jobs:
            if job.is_locked:
                is_deployable = False

        for module in self.project.modules:
            if module.is_locked:
                is_deployable = False

        if not is_deployable:
            print("Active edits in superglue project. Please run superglue package to update the version.")
            print("Deployment not possible")
            exit(1)
        else:
            print("Superglue project is up to date. Deployment is possible")
            exit(0)
