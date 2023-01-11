from superglue.cli.utils import validate_account
from superglue.cli.base import BaseSuperglueCommand
from superglue.cli.messages import Messages

__version__ = "0.11.0"


class Version(BaseSuperglueCommand):

    help = "--> Print the current version of superglue and exit."

    def __call__(self) -> None:
        print(f"The AWS Glue Deployment Utility -- superglue version :: {__version__}")


class Account(BaseSuperglueCommand):

    help = "--> Print the AWS account number that superglue is configured to use."

    @validate_account
    def __call__(self) -> None:
        pass


class Init(BaseSuperglueCommand):

    help = "--> Creates a new superglue project structure."

    def __call__(self) -> None:
        self.project.create()
        Messages.project_initialized()


class New(BaseSuperglueCommand):

    help = "--> Creates a new superglue job or module"

    args = {
        ("component_type",): {"choices": ["job", "module"], "help": "Can be either job or module"},
        ("-n", "--name"): {"required": True, "help": "The name of the new component to create"},
    }

    def __call__(self) -> None:

        component = getattr(self.project, self.cli_args.component_type).new(self.cli_args.name)
        messages = Messages(component)

        if component.component_path.exists():
            messages.component_exists()
            exit(1)

        else:
            component.save()
            messages.component_created()
            exit(0)


class Check(BaseSuperglueCommand):

    help = "--> Used to check the status of the superglue project before a deployment"

    @validate_account
    def __call__(self) -> None:

        if not self.project.is_locked():
            Messages.no_deployment()
            exit(1)

        if self.project.modules.are_not_packaged():
            Messages.not_packaged()
            exit(1)

        else:
            Messages.yes_deployment()


class Lock(BaseSuperglueCommand):

    help = "--> Lock superglue jobs and modules to the next version if they have active edits."

    def __call__(self) -> None:

        Messages.locking_jobs()

        if self.project.jobs.are_unlocked():
            for job in self.project.jobs.unlocked():
                Messages.locking_job(job)
                job.lock()
        else:
            Messages.all_jobs_locked()

        Messages.locking_modules()

        if self.project.modules.are_unlocked():
            for module in self.project.modules.unlocked():
                Messages.locking_module(module)
                module.lock()
        else:
            Messages.all_modules_locked()


class Package(BaseSuperglueCommand):

    help = "--> Packages all superglue jobs and modules which have been edited since the last package was issued."

    args = {("-p", "--purge"): {"action": "store_true", "default": False}}

    def __call__(self) -> None:

        if self.cli_args.purge:
            self.purge()

        else:
            self.lock_check()
            self.package()

    def purge(self) -> None:
        for module in self.project.modules:
            module.remove_zipfile()
            Messages.removed_zipfile(module)
        Messages.purge_complete()
        exit(0)

    def lock_check(self) -> None:
        if self.project.modules.are_unlocked():
            Messages.modules_not_locked()
            exit(1)

    def package(self) -> None:
        for module in self.project.modules:
            module.package()
            Messages.packaging_module(module.name)
        Messages.packaging_complete()
        exit(0)


class Status(BaseSuperglueCommand):

    help = "--> Prints the current status of all superglue jobs and modules."

    args = {
        ("-m", "--modules"): {"action": "store_true", "default": False, "dest": "only_modules"},
        ("-j", "--jobs"): {"action": "store_true", "default": False, "dest": "only_jobs"},
    }

    @validate_account
    def __call__(self) -> None:
        table = self.project.get_pretty_table()

        if not self.cli_args.only_jobs:
            for module in self.project.modules:
                table.add_row(module.pretty_table_row)

        if not self.cli_args.only_modules:
            for job in self.project.jobs:
                table.add_row(job.pretty_table_row)

        print(table)


class Deploy(BaseSuperglueCommand):

    help = "--> Deploys all superglue jobs and modules which have been changed since the last issued deployment."

    args = {
        ("-d", "--dry"): {
            "action": "store_true",
            "default": False,
            "help": "Print a dry run to the terminal of what superglue would deploy",
        }
    }

    @validate_account
    def __call__(self) -> None:

        if not self.project.is_locked():
            Messages.no_deployment()
            exit(1)

        if self.project.modules.are_not_packaged():
            Messages.not_packaged()
            exit(1)

        if self.cli_args.dry:
            Messages.dry_run()
            self.dry_module_deploy()
            self.dry_job_deploy()
            exit(0)

        Messages.yes_deployment()
        self.module_deploy()
        self.job_deploy()

    def dry_module_deploy(self) -> None:
        for module in self.project.modules.deployable():
            Messages.module_deploy(module, dry=True)

    def dry_job_deploy(self) -> None:
        for job in self.project.jobs.deployable():
            job.generate_deployment_yml()
            Messages.job_deploy(job, dry=True)

    def module_deploy(self) -> None:
        for module in self.project.modules.deployable():
            module.deploy()
            Messages.module_deploy(module)

    def job_deploy(self) -> None:
        for job in self.project.jobs.deployable():
            job.deploy()
            Messages.job_deploy(job)


class Generate(BaseSuperglueCommand):

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
