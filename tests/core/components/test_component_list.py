import pytest
from typing import List
from unittest.mock import MagicMock
from superglue.core.components.component_list import SuperglueComponentList


@pytest.fixture()
def mock_components() -> List[MagicMock]:
    mm1 = MagicMock()
    mm2 = MagicMock()
    mm3 = MagicMock()

    mm1.is_locked = True
    mm2.is_locked = True
    mm3.is_locked = False

    mm1.is_deployable = True
    mm2.is_deployable = False
    mm3.is_deployable = False

    return [mm1, mm2, mm3]


def test_inherits_list() -> None:
    assert issubclass(SuperglueComponentList, list)


def test_edited_filter(mock_components: List[MagicMock]) -> None:
    component_list = SuperglueComponentList(mock_components)
    results = component_list.locked()
    assert results == [mock_components[0], mock_components[1]]
    assert isinstance(results, list)


def test_deployable(mock_components: List[MagicMock]) -> None:
    component_list = SuperglueComponentList(mock_components)
    results = component_list.deployable()
    assert results == [mock_components[0]]
    assert isinstance(results, list)
