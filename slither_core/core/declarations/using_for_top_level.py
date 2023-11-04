from typing import TYPE_CHECKING, List, Dict, Union

from slither_core.core.declarations.contract import USING_FOR_KEY, USING_FOR_ITEM
from slither_core.core.solidity_types.type import Type
from slither_core.core.declarations.top_level import TopLevel

if TYPE_CHECKING:
    from slither_core.core.scope.scope import FileScope


class UsingForTopLevel(TopLevel):
    def __init__(self, scope: "FileScope") -> None:
        super().__init__()
        self._using_for: Dict[Union[str, Type], List[Type]] = {}
        self.file_scope: "FileScope" = scope

    @property
    def using_for(self) -> Dict[USING_FOR_KEY, USING_FOR_ITEM]:
        return self._using_for
