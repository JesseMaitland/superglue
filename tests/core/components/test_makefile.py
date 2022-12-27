import pytest
from pathlib import Path
from unittest.mock import patch
from superglue.environment.config import TOOLS_PATH
from superglue.core.components.makefile import SuperglueMakefile


@pytest.fixture(scope="module")
def makefile() -> SuperglueMakefile:
    return SuperglueMakefile()


def test_makefile_component_type(makefile: SuperglueMakefile) -> None:
    assert makefile.component_type == "superglue_tool"


def test_makefile_component_name(makefile: SuperglueMakefile) -> None:
    assert makefile.component_name == "makefile"


def test_makefile_tools_path(makefile: SuperglueMakefile) -> None:
    assert makefile.root_dir == TOOLS_PATH


def test_makefile_root_makefile(makefile: SuperglueMakefile) -> None:
    assert makefile.root_makefile == Path.cwd().joinpath("makefile")


def test_makefile_path(makefile: SuperglueMakefile) -> None:
    assert makefile.makefile_path == TOOLS_PATH.joinpath("makefile")


def test_makefile_new(makefile: SuperglueMakefile) -> None:
    assert isinstance(SuperglueMakefile.new(), SuperglueMakefile)


def test_save_root_makefile() -> None:
    with patch.object(SuperglueMakefile, "root_makefile") as p_makefile:
        makefile = SuperglueMakefile()
        makefile.save_root_makefile()

        assert p_makefile.touch.assert_called_with(exist_ok=True)

