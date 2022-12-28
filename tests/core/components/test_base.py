import pytest
from pathlib import Path
from jinja2 import Environment, PackageLoader
from superglue.core.components.base import BaseSuperglueComponent, SuperglueComponent


class _BaseSuperglueComponent(BaseSuperglueComponent):
    def save(self) -> None:
        pass


class _SuperglueComponent(SuperglueComponent):
    def save(self) -> None:
        pass

    def delete(self) -> None:
        pass

    def deploy(self) -> None:
        pass


EXPECTED_TEMPLATES = [
    "__init__.py",
    "conftest.template.py",
    "job_config.template.yml",
    "job_test.template.py.txt",
    "main.template.py",
    "makefile",
    "module_test.template.py.txt",
    "template.env",
    "template.gitignore",
]


@pytest.fixture(scope="module")
def base_component() -> BaseSuperglueComponent:
    return _BaseSuperglueComponent(root_dir=Path.cwd(), component_name="foo", component_type="bar")


@pytest.fixture(scope="module")
def superglue_component() -> SuperglueComponent:
    return _SuperglueComponent(
        root_dir=Path.cwd(),
        component_type="eggs",
        component_name="spam",
        bucket="spam-eggs-sausage-and-spam",
        iam_role="The-Almighty-God-Himself",
    )


def test_base_component_name(base_component: BaseSuperglueComponent) -> None:
    assert base_component.component_name == "foo"


def test_base_component_type(base_component: BaseSuperglueComponent) -> None:
    assert base_component.component_type == "bar"


def test_base_component_root_dir(base_component: BaseSuperglueComponent) -> None:
    assert base_component.root_dir == Path.cwd()


def test_base_component_path(base_component: BaseSuperglueComponent) -> None:
    assert base_component.component_path == base_component.root_dir / base_component.component_name


def test_base_component_eq(base_component: BaseSuperglueComponent) -> None:
    bc = _BaseSuperglueComponent(Path.cwd(), "foo", "bar")
    assert bc == base_component


def test_base_component_not_eq(base_component: BaseSuperglueComponent) -> None:
    bc = _BaseSuperglueComponent(Path.cwd(), "spam", "bar")
    assert bc != base_component


def test_base_component_jinja_method(base_component: BaseSuperglueComponent) -> None:
    assert hasattr(base_component, "get_jinja_environment")


def test_base_component_get_jinja_environment(base_component: BaseSuperglueComponent) -> None:
    jinja = base_component.get_jinja_environment()
    assert isinstance(jinja, Environment)


def test_base_component_jinja_environment(base_component: BaseSuperglueComponent) -> None:
    jinja = base_component.get_jinja_environment()
    assert isinstance(jinja.loader, PackageLoader)


def test_base_component_jinja_environment_config(base_component: BaseSuperglueComponent) -> None:
    jinja = base_component.get_jinja_environment()
    assert jinja.trim_blocks is True
    assert jinja.lstrip_blocks is True


def test_base_component_jinja_environment_loader(base_component: BaseSuperglueComponent) -> None:
    jinja = base_component.get_jinja_environment()
    assert jinja.loader.package_name == "superglue"
    assert jinja.loader.package_path == "templates"


def test_base_component_jinja_environment_templates(base_component: BaseSuperglueComponent) -> None:
    jinja = base_component.get_jinja_environment()
    assert jinja.loader.list_templates() == EXPECTED_TEMPLATES


def test_superglue_component_name(superglue_component: SuperglueComponent) -> None:
    assert superglue_component.component_name == "spam"


def test_superglue_component_type(superglue_component: SuperglueComponent) -> None:
    assert superglue_component.component_type == "eggs"


def test_superglue_component_root_dir(superglue_component: SuperglueComponent) -> None:
    assert superglue_component.root_dir == Path.cwd()


def test_superglue_component_bucket(superglue_component: SuperglueComponent) -> None:
    assert superglue_component.bucket == "spam-eggs-sausage-and-spam"


def test_superglue_component_iam_role(superglue_component: SuperglueComponent) -> None:
    assert superglue_component.iam_role == "The-Almighty-God-Himself"


def test_superglue_component_version(superglue_component: SuperglueComponent) -> None:
    assert superglue_component.version == {}


def test_superglue_component_version_number(superglue_component: SuperglueComponent) -> None:
    assert superglue_component.version_number == 0


def test_superglue_component_version_file(superglue_component: SuperglueComponent) -> None:
    assert superglue_component.version_file == superglue_component.component_path / ".version"


def test_superglue_component_s3_path(superglue_component: SuperglueComponent) -> None:
    s3_path = "s3://spam-eggs-sausage-and-spam/superglue/eggs/spam/version=0/spam"
    assert superglue_component.s3_path == s3_path


def test_superglue_component_s3_prefix(superglue_component: SuperglueComponent) -> None:
    s3_prefix = "superglue/eggs/spam/version=0"
    assert superglue_component.s3_prefix == s3_prefix


def test_superglue_component_s3_version_path(superglue_component: SuperglueComponent) -> None:
    version_path = "superglue/eggs/spam/version=0/spam/.version"
    assert superglue_component.s3_version_path == version_path
