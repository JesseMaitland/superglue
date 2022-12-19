import pytest
from pathlib import Path
from unittest.mock import MagicMock, patch
from superglue.core.components.base import SuperglueComponent
from superglue.core.components.files import SuperglueFiles


@pytest.fixture(scope="module")
def files() -> SuperglueFiles:
    return SuperglueFiles()


def test_superglue_files_inheritance() -> None:
    assert issubclass(SuperglueFiles, SuperglueComponent)


def test_gitignore_property(files: SuperglueFiles) -> None:
    cwd = Path.cwd()
    assert cwd.joinpath(".gitignore") == files.gitignore_file


def test_dotenv_file_property(files: SuperglueFiles) -> None:
    cwd = Path.cwd()
    assert cwd.joinpath(".env") == files.dotenv_file


def test_files_property(files: SuperglueFiles) -> None:
    assert isinstance(files.files, list)


def test_files_paths(files: SuperglueFiles) -> None:
    for file in files.files:
        assert isinstance(file, Path)
