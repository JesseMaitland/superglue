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
def test_module_get_class_method_ex(module_root_path: MagicMock) -> None:
    module_root_path.exists.return_value = False
    with pytest.raises(FileNotFoundError):
        _ = SuperglueModule.get("foo")


@patch.object(SuperglueModule, "module_root_path")
def test_module_from_version_class_method(module_root_path: MagicMock) -> None:
    module_root_path.exists.return_value = True
    module = SuperglueModule.from_version("beast", 666)
    assert module.name == "beast"
    assert module.version_number == 666


@patch.object(SuperglueModule, "module_root_path")
def test_module_from_version_class_method_ex(module_root_path: MagicMock) -> None:
    module_root_path.exists.return_value = False
    with pytest.raises(FileNotFoundError):
        _ = SuperglueModule.from_version("bar", 1)


@patch.object(SuperglueModule, "save_tests")
@patch.object(SuperglueModule, "save_version_file")
@patch.object(SuperglueModule, "module_inner_path")
def test_module_save_method(module_inner_path, save_version_file, save_tests) -> None:
    mock_path = MagicMock()
    module_inner_path.__truediv__.return_value = mock_path

    module = SuperglueModule("spam")
    module.save()

    mock_path.touch.assert_called_once_with(exist_ok=True)
    save_version_file.assert_called_once()
    save_tests.assert_called_once()


@patch.object(SuperglueModule, "append_version")
@patch.object(SuperglueModule, "sync")
def test_module_deploy_method(sync: MagicMock, _) -> None:
    module = SuperglueModule("foo")
    module.deploy(False)
    sync.assert_called_once()


def test_module_delete_not_implemented(module: SuperglueModule) -> None:
    with pytest.raises(NotImplementedError):
        module.delete()


def test_module_zipfile_relative_path_method(module: SuperglueModule) -> None:
    path = MagicMock()
    relative_to = MagicMock()
    path.relative_to.return_value = relative_to

    _ = module.zipfile_relative_path(path)
    path.relative_to.assert_called_once_with(module.module_root_path)
    relative_to.as_posix.assert_called_once()


def test_module_zipfile_content_method(module: SuperglueModule) -> None:
    path = MagicMock()
    _ = module.zipfile_content(path)
    path.read_text.assert_called_once_with(encoding="utf-8")


@patch.object(SuperglueModule, "module_files")
@patch.object(SuperglueModule, "zipfile_relative_path")
@patch.object(SuperglueModule, "zipfile_content")
@patch("superglue.core.components.module.zipfile.ZipFile")
def test_module_package_method(
    zipfile: MagicMock, zipfile_content: MagicMock, zipfile_relative_path: MagicMock, module_files: MagicMock
) -> None:
    content = "This is the content"
    path_value = "/spam/eggs"
    zipfile_file = MagicMock()
    module_files_files = MagicMock()
    module_files.return_value = [module_files_files]

    zipfile.return_value.__enter__.return_value = zipfile_file
    zipfile_content.return_value = content
    zipfile_relative_path.return_value = path_value

    module = SuperglueModule("beans")
    module.package()

    zipfile_content.assert_called_once_with(module_files_files)
    zipfile_relative_path.assert_called_once_with(module_files_files)

    zipfile_file.writestr.assert_called_once_with(path_value, content)


@patch.object(SuperglueModule, "zipfile")
def test_module_remove_zipfile_true(zipfile: MagicMock) -> None:
    zipfile.exists.return_value = True
    module = SuperglueModule("bananas")
    module.remove_zipfile()

    zipfile.unlink.assert_called_once()


@patch.object(SuperglueModule, "zipfile")
def test_module_remove_zipfile_false(zipfile: MagicMock) -> None:
    zipfile.exists.return_value = False
    module = SuperglueModule("bananas")
    module.remove_zipfile()

    zipfile.unlink.assert_not_called()
