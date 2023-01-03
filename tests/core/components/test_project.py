import pytest
from prettytable import PrettyTable
from unittest.mock import MagicMock, patch
from superglue.core.components.project import SuperglueProject
from superglue.core.components.job import SuperglueJob
from superglue.core.components.module import SuperglueModule
from superglue.core.components.component_list import SuperglueComponentList
from superglue.environment.config import JOBS_PATH, MODULES_PATH, NOTEBOOKS_PATH, TOOLS_PATH
from superglue.core.components.makefile import SuperglueMakefile
from superglue.core.components.tests import SuperglueTests
from superglue.core.components.files import SuperglueFiles


EXPECTED_PRETTY_TABLE_FIELDS = ["Component Name", "Component Type", "Local Stats", "s3 Status", "Version Number"]


@pytest.fixture(scope="module")
def project() -> SuperglueProject:
    return SuperglueProject()


def test_jobs_path_property(project: SuperglueProject) -> None:
    assert project.jobs_path == JOBS_PATH


def test_modules_path_property(project: SuperglueProject) -> None:
    assert project.modules_path == MODULES_PATH


def test_notebooks_path_property(project: SuperglueProject) -> None:
    assert project.notebooks_path == NOTEBOOKS_PATH


def test_tools_path_property(project: SuperglueProject) -> None:
    assert project.tools_path == TOOLS_PATH


def test_job_property(project: SuperglueProject) -> None:
    assert issubclass(SuperglueJob, project.job)


def test_project_dirs_property(project: SuperglueProject) -> None:
    expected = [JOBS_PATH, MODULES_PATH, NOTEBOOKS_PATH, TOOLS_PATH]
    assert expected == project.project_dirs


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


def test_makefile_property(project: SuperglueProject) -> None:
    assert issubclass(SuperglueMakefile, project.makefile)


def test_files_property(project: SuperglueProject) -> None:
    assert issubclass(SuperglueFiles, project.files)


def test_tests_property(project: SuperglueProject) -> None:
    assert issubclass(SuperglueTests, project.tests)


def test_pretty_table_fields_property(project: SuperglueProject) -> None:
    assert EXPECTED_PRETTY_TABLE_FIELDS == project.pretty_table_fields


def test_save_component_method() -> None:
    with patch.object(SuperglueProject, "makefile") as p_makefile:
        project = SuperglueProject()

        m_makefile = MagicMock()
        p_makefile.new.return_value = m_makefile

        project.save_project_component("makefile")
        p_makefile.new.assert_called_once()
        m_makefile.save.assert_called_once()


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


def test_save_base_project() -> None:
    with patch.object(SuperglueProject, "project_dirs") as project_dirs:
        mock_dirs = [MagicMock()]
        project_dirs.__iter__.return_value = mock_dirs

        project = SuperglueProject()
        project.save_base_project()

        mock_dirs[0].mkdir.assert_called_once_with(exist_ok=True)


def test_save_project_components() -> None:
    with patch.object(SuperglueProject, "save_project_component") as save_project_component:
        project = SuperglueProject()
        project.save_project_components()

        save_project_component.assert_any_call("makefile")
        save_project_component.assert_any_call("files")
        save_project_component.assert_any_call("tests")


def test_create_project_method() -> None:
    with patch.object(SuperglueProject, "save_base_project") as save_base_project:
        with patch.object(SuperglueProject, "save_project_components") as save_project_components:
            project = SuperglueProject()
            project.create()

            save_base_project.assert_called_once()
            save_project_components.assert_called_once()
