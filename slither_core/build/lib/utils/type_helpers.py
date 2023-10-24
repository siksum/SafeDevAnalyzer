from typing import Union, Tuple, TYPE_CHECKING

if TYPE_CHECKING:
    from slither_core.core.declarations import (
        Function,
        SolidityFunction,
        Contract,
        SolidityVariable,
    )
    from slither_core.core.variables.variable import Variable

# core.declaration
# pylint: disable=used-before-assignment
InternalCallType = Union["Function", "SolidityFunction"]
HighLevelCallType = Tuple["Contract", Union["Function", "Variable"]]
LibraryCallType = Tuple["Contract", "Function"]
LowLevelCallType = Tuple[Union["Variable", "SolidityVariable"], str]
