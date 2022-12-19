import {{module}}
from zipimport import zipimporter


def test_module_{{module}}_is_ziptype() -> None:
    loader = {{module}}.__spec__.loader
    assert isinstance(loader, zipimporter)
