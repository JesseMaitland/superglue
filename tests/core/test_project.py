import pytest
from unittest.mock import MagicMock
from pathlib import Path
from superglue.core.project import SuperGlueProject


@pytest.fixture
def project() -> SuperGlueProject:
    return SuperGlueProject()


def test_jobs_root_directory(project: SuperGlueProject) -> None:
    assert project.jobs_root == Path.cwd() / "glue_jobs"


def test_shared_root_directory(project: SuperGlueProject) -> None:
    assert project.shared_root == Path.cwd() / "shared"


def test_notebooks_directory(project: SuperGlueProject) -> None:
    assert project.notebooks == Path.cwd() / "notebooks"


def test_create_method(project: SuperGlueProject) -> None:
    project.jobs_root = MagicMock()
    project.shared_root = MagicMock()
    project.notebooks = MagicMock()
    project.makefile_template = MagicMock()

    project.create()

    project.jobs_root.mkdir.assert_called_once_with(exist_ok=True)
    project.shared_root.mkdir.assert_called_once_with(exist_ok=True)
    project.notebooks.mkdir.assert_called_once_with(exist_ok=True)


def test_script_path(project: SuperGlueProject) -> None:
    pass
