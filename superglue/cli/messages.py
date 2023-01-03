from typing import Optional
from superglue.core.components.base import SuperglueComponentType
from superglue.core.components.job import SuperglueJobType
from superglue.core.components.module import SuperglueModuleType


class Messages:
    def __init__(self, component: SuperglueComponentType) -> None:
        self.component = component

    @staticmethod
    def project_initialized() -> None:
        print("Superglue project has been created successfully!")

    @staticmethod
    def modules_locked() -> None:
        print("All superglue modules are locked")

    @staticmethod
    def modules_not_locked() -> None:
        print("Not all superglue modules are locked. Please lock them with the superglue lock command.")

    @staticmethod
    def jobs_locked() -> None:
        print("All superglue jobs are locked.")

    @staticmethod
    def jobs_not_locked() -> None:
        print("Not all superglue jobs are locked. Please lock them with the superglue lock command.")

    @staticmethod
    def packaging_module(name: str, dry: Optional[bool] = False) -> None:
        pre = ""
        if dry:
            pre = "-- Dry Run -- "
        print(f"{pre}Packaging superglue module :: {name}")

    @staticmethod
    def locking_jobs() -> None:
        print("\n------------------> Locking Superglue Jobs <------------------\n")

    @staticmethod
    def locking_modules() -> None:
        print("\n------------------> Locking Superglue Modules <------------------\n")

    @staticmethod
    def locking_job(job: SuperglueJobType) -> None:
        print(f"Locking Job -----> {job.name} :: Version {job.next_version_number}")

    @staticmethod
    def locking_module(module: SuperglueModuleType) -> None:
        print(f"Locking module -----> {module.name} :: Version {module.next_version_number}")

    @staticmethod
    def no_deployment() -> None:
        print("Unlocked modules or jobs exist. Deployment is not possible.")

    @staticmethod
    def yes_deployment() -> None:
        print("All superglue jobs and modules are up to date. Deployment is possible.")

    @staticmethod
    def removed_zipfile(module: SuperglueModuleType) -> None:
        print(f"Removed zip package for superglue module {module.name}")

    @staticmethod
    def purge_complete() -> None:
        print("Purging superglue module zipfiles done.")

    @staticmethod
    def packaging_complete() -> None:
        print("Packaging superglue modules done.")

    @staticmethod
    def nothing_to_deploy() -> None:
        print("Everything up to date in S3. Nothing to Deploy.")

    @staticmethod
    def dry_run() -> None:
        print("\n----------------------->> DEPLOYMENT DRY RUN <<-----------------------\n")

    @staticmethod
    def job_deploy(job: SuperglueJobType, dry: Optional[bool] = False) -> None:
        pre = ""
        if dry:
            pre = "-- Dry Run -- "

        print(f"{pre}Superglue job {job.name} deployed to the following location.")
        print(job.s3_path)
        print("\n")

    @staticmethod
    def module_deploy(module: SuperglueModuleType, dry: Optional[bool] = False) -> None:
        pre = ""
        if dry:
            pre = "-- Dry Run -- "

        print(f"{pre}Superglue module {module.name} deployed to the following location.")
        print(module.s3_path)
        print("\n")

    @staticmethod
    def not_packaged() -> None:
        print("There are unpackaged modules present. Deployment not possible.")

    @staticmethod
    def all_jobs_locked() -> None:
        print("All superglue jobs are locked")

    @staticmethod
    def all_modules_locked() -> None:
        print("All superglue modules are locked")

    def component_exists(self) -> None:
        print(f"{self.component.component_type.capitalize()} {self.component.component_name} already exists.")

    def component_created(self) -> None:
        print(
            f"{self.component.component_type.capitalize()} {self.component.component_name} has been created successfully."
        )
