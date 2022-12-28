import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock
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


def test_makefile_save_root_makefile() -> None:
    with patch.object(SuperglueMakefile, "root_makefile") as p_root_makefile:
        makefile = SuperglueMakefile()
        makefile.save_root_makefile()

        p_root_makefile.touch.assert_called_once_with(exist_ok=True)
        p_root_makefile.write_text.assert_called_once_with("include tools/makefile")


def test_makefile_save_tools_makefile() -> None:
    with patch.object(SuperglueMakefile, "makefile_path") as p_makefile_path:
        content = "foo-bar-baz"
        makefile = SuperglueMakefile()
        makefile.save_tools_makefile(content)

        p_makefile_path.touch.assert_called_once_with(exist_ok=True)
        p_makefile_path.write_text.assert_called_once_with(content)


def test_makefile_get_tools_makefile_content(makefile: SuperglueMakefile) -> None:
    jinja2 = makefile.get_jinja_environment()
    content = jinja2.get_template("makefile").render()
    assert content == makefile.get_tools_makefile_content()
