import pytest
from unittest.mock import MagicMock, patch
from pathlib import Path
from superglue.core._project import SuperGlueProject


@pytest.fixture
def project() -> SuperGlueProject:
    return SuperGlueProject()


def test_jobs_root_directory(project: SuperGlueProject) -> None:
    assert project.jobs_path == Path.cwd() / "glue_jobs"


def test_shared_root_directory(project: SuperGlueProject) -> None:
    assert project.shared_path == Path.cwd() / "shared"


def test_notebooks_directory(project: SuperGlueProject) -> None:
    assert project.notebooks_path == Path.cwd() / "notebooks"


@patch("superglue.core.project.Path")
def test_create_method(_, project: SuperGlueProject) -> None:
    project.jobs_root = MagicMock()
    project.shared_root = MagicMock()
    project.notebooks = MagicMock()
    project.makefile_template = MagicMock()

    project.create()

    project.jobs_path.mkdir.assert_called_once_with(exist_ok=True)
    project.shared_path.mkdir.assert_called_once_with(exist_ok=True)
    project.notebooks_path.mkdir.assert_called_once_with(exist_ok=True)


def test_script_path(project: SuperGlueProject) -> None:
    pass
