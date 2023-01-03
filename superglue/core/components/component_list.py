from typing import List
from superglue.core.components.base import SuperglueComponentType


class SuperglueComponentList(list):
    def deployable(self) -> List[SuperglueComponentType]:
        return [c for c in self if c.is_deployable]

    def locked(self) -> List[SuperglueComponentType]:
        return [c for c in self if c.is_locked]

    def unlocked(self) -> List[SuperglueComponentType]:
        return [c for c in self if c.is_unlocked]

    def are_locked(self) -> bool:
        locked_status = [c.is_locked for c in self]
        return not False in locked_status

    def are_unlocked(self) -> bool:
        return not self.are_locked()

    def are_packaged(self) -> bool:
        packaged_status = [c.is_packaged for c in self]
        return not False in packaged_status

    def are_not_packaged(self) -> bool:
        return not self.are_packaged()
