import pytest
from unittest.mock import patch, MagicMock
from superglue.core.components.job import SuperglueJob
from superglue.core.components.tests import SuperglueTests
from superglue.environment.config import MODULES_PATH, TESTS_PATH

TEST_JOB_NAME = "a_link_to_the_past"


@pytest.fixture(scope="module")
def job() -> SuperglueJob:
    return SuperglueJob(job_name=TEST_JOB_NAME)


def test_job_job_path_property(job: SuperglueJob) -> None:
    assert job.job_path == job.root_dir / job.name


def test_job_pys_path_property(job: SuperglueJob) -> None:
    assert job.pys_path == job.job_path / "py"


def test_job_jars_path_property(job: SuperglueJob) -> None:
    assert job.jars_path == job.job_path / "jars"


def test_job_job_test_path_property(job: SuperglueJob) -> None:
    assert job.job_test_path == job.tests.jobs_test_dir / job.name


def test_job_main_script_file_property(job: SuperglueJob) -> None:
    assert job.main_script_file == job.job_path / "main.py"


def test_job_config_file_property(job: SuperglueJob) -> None:
    assert job.config_file == job.job_path / "config_base.yml"


def test_job_overrides_file_property(job: SuperglueJob) -> None:
    assert job.overrides_file == job.job_path / "config_overrides.yml"


def test_job_deployment_config_file(job: SuperglueJob) -> None:
    assert job.deployment_config_file == job.job_path / "config_merged.yml"


def test_job_superglue_modules_property() -> None:
    mock = MagicMock()

    job = SuperglueJob(job_name="foo")
    job.config = mock
    _ = job.superglue_modules

    mock.get.assert_called_once_with("superglue_modules", {})
