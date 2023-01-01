from typing import List
from superglue.core.types import SuperglueComponentType


class SuperglueComponentList(list):
    def edited(self) -> List[SuperglueComponentType]:
        return [c for c in self if c.is_unlocked]

    def deployable(self) -> List[SuperglueComponentType]:
        return [c for c in self if c.is_deployable]

    def locked(self) -> List[SuperglueComponentType]:
        return [c for c in self if c.is_locked]

    def unlocked(self) -> List[SuperglueComponentType]:
        return [c for c in self if c.is_unlocked]

    def are_locked(self) -> bool:
        locked_status = [c.is_locked for c in self]
        return not False in locked_status
