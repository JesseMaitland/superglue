import pytest
from unittest.mock import patch, MagicMock
from superglue.core.components.module import SuperglueModule
from superglue.core.components.tests import SuperglueTests
from superglue.environment.config import MODULES_PATH, TESTS_PATH

TEST_MODULE_NAME = "green_eggs_and_ham"
TEST_ZIPFILE_NAME = f"{TEST_MODULE_NAME}.zip"

@pytest.fixture()
def module() -> SuperglueModule:
    return SuperglueModule(name=TEST_MODULE_NAME)


def test_module_root_path_property(module: SuperglueModule) -> None:
    assert module.module_root_path == MODULES_PATH / TEST_MODULE_NAME


def test_module_inner_path_property(module: SuperglueModule) -> None:
    assert module.module_inner_path == MODULES_PATH / TEST_MODULE_NAME / TEST_MODULE_NAME


def test_module_zipfile_property(module: SuperglueModule) -> None:
    assert module.zipfile == MODULES_PATH / TEST_MODULE_NAME / TEST_ZIPFILE_NAME


def test_module_s3_zipfile_path_property(module: SuperglueModule) -> None:
    assert module.s3_zipfile_path == f"{module.s3_path}/{TEST_ZIPFILE_NAME}"


def test_module_test_path_property(module: SuperglueModule) -> None:
    assert module.module_test_path == TESTS_PATH / "modules" / TEST_MODULE_NAME


def test_module_test_file_property(module: SuperglueModule) -> None:
    assert module.module_tests_file == module.module_test_path / f"test_{TEST_MODULE_NAME}.py"


def test_module_is_packaged_property(module: SuperglueModule) -> None:
    assert module.is_packaged == module.zipfile.exists()


def test_module_tests_property(module: SuperglueModule) -> None:
    assert isinstance(module.tests, SuperglueTests)


def test_module_new_class_method() -> None:
    module = SuperglueModule.new("foo")
    assert isinstance(module, SuperglueModule)
    assert module.name == "foo"


@patch.object(SuperglueModule, "module_root_path")
def test_module_get_class_method(module_root_path: MagicMock) -> None:
    module_root_path.exists.return_value = True
    module = SuperglueModule.get("foo")
    assert isinstance(module, SuperglueModule)


@patch.object(SuperglueModule, "module_root_path")
def test_module_get_class_method(module_root_path: MagicMock) -> None:
    module_root_path.exists.return_value = False
    with pytest.raises(FileNotFoundError):
        _ = SuperglueModule.get("foo")

@patch.object(SuperglueModule, "module_root_path")
def test_module_from_version_class_method(module_root_path: MagicMock) -> None:
    module_root_path.exists.return_value = True
    module = SuperglueModule.from_version("beast", 666)
    assert module.name == "beast"
    assert module.version_number == 666

@patch.object(SuperglueModule, "sync")
def test_module_deploy_method(sync: MagicMock) -> None:
    module = SuperglueModule("foo")
    module.deploy()
    sync.assert_called_once()
