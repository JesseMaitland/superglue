import pytest
from pathlib import Path
from prettytable import PrettyTable
from unittest.mock import MagicMock, patch
from superglue.core.components.project import SuperglueProject
from superglue.core.components.job import SuperglueJob
from superglue.core.components.module import SuperglueModule
from superglue.core.components.component_list import SuperglueComponentList
from superglue.environment.config import JOBS_PATH, MODULES_PATH, NOTEBOOKS_PATH


EXPECTED_PRETTY_TABLE_FIELDS = ["Component Name", "Component Type", "Local Stats", "s3 Status", "Version Number"]


@pytest.fixture(scope="module")
def project() -> SuperglueProject:
    return SuperglueProject()


def test_jobs_root_directory(project: SuperglueProject) -> None:
    assert project.jobs_path == Path.cwd() / "glue_jobs"


def test_shared_root_directory(project: SuperglueProject) -> None:
    assert project.modules_path == Path.cwd() / "glue_modules"


def test_notebooks_directory(project: SuperglueProject) -> None:
    assert project.notebooks_path == Path.cwd() / "notebooks"


def test_jobs_path_property(project: SuperglueProject) -> None:
    assert project.jobs_path == JOBS_PATH


def test_modules_path_property(project: SuperglueProject) -> None:
    assert project.modules_path == MODULES_PATH


def test_notebooks_path_property(project: SuperglueProject) -> None:
    assert project.notebooks_path == NOTEBOOKS_PATH


def test_job_property(project: SuperglueProject) -> None:
    assert issubclass(SuperglueJob, project.job)


def test_jobs_property() -> None:
    with patch.object(SuperglueProject, "job") as m_job:
        with patch.object(SuperglueProject, "jobs_path") as m_jobs_path:
            project = SuperglueProject()
            mock_job = MagicMock()

            mock_path = MagicMock()
            mock_path.name = "watermelon"

            m_jobs_path.iterdir.return_value = [mock_path]

            m_job.get.return_value = mock_job

            jobs = project.jobs

            m_job.get.assert_called_once_with("watermelon")
            m_jobs_path.iterdir.assert_called()

            assert isinstance(jobs, SuperglueComponentList)


def test_module_property(project: SuperglueProject) -> None:
    assert issubclass(SuperglueModule, project.module)


def test_modules_property() -> None:
    with patch.object(SuperglueProject, "module") as m_module:
        with patch.object(SuperglueProject, "modules_path") as m_modules_path:
            project = SuperglueProject()
            mock_module = MagicMock()

            mock_path = MagicMock()
            mock_path.name = "banana"

            m_modules_path.iterdir.return_value = [mock_path]

            m_module.get.return_value = mock_module

            modules = project.modules

            m_module.get.assert_called_once_with("banana")
            m_modules_path.iterdir.assert_called()

            assert isinstance(modules, SuperglueComponentList)


def test_pretty_table_fields_property(project: SuperglueProject) -> None:
    assert EXPECTED_PRETTY_TABLE_FIELDS == project.pretty_table_fields


def test_pretty_table(project: SuperglueProject) -> None:
    table = project.get_pretty_table()
    assert table.field_names == EXPECTED_PRETTY_TABLE_FIELDS
    assert table.align["Version Number"] == "c"
    assert table.align["Component Name"] == "l"
    assert table.align["Component Type"] == "l"
    assert table.align["Local Stats"] == "l"
    assert table.align["s3 Status"] == "l"
    assert table.sortby == "Component Type"

    assert isinstance(table, PrettyTable)


def test_makefile_template_path(project: SuperglueProject) -> None:
    template_path = "/superglue/core/"
    print(project.makefile_template.as_posix())
