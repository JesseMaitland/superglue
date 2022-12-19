from typing import List
from superglue.core.components.base import SuperglueComponentType


class SuperglueComponentList(list):
    def edited(self) -> List[SuperglueComponentType]:
        return [c for c in self if c.is_edited]

    def deployable(self) -> List[SuperglueComponentType]:
        return [c for c in self if c.is_deployable]
