from typing import Union, Optional

from slither_core.core.variables.local_variable import LocalVariable
from slither_core.core.variables.state_variable import StateVariable

from slither_core.core.declarations.solidity_variables import SolidityVariable
from slither_core.core.variables.top_level_variable import TopLevelVariable

from slither_core.slithir.variables.temporary import TemporaryVariable
from slither_core.slithir.variables.constant import Constant
from slither_core.slithir.variables.reference import ReferenceVariable
from slither_core.slithir.variables.tuple import TupleVariable
from slither_core.core.source_mapping.source_mapping import SourceMapping

RVALUE = Union[
    StateVariable,
    LocalVariable,
    TopLevelVariable,
    TemporaryVariable,
    Constant,
    SolidityVariable,
    ReferenceVariable,
]

LVALUE = Union[
    StateVariable,
    LocalVariable,
    TemporaryVariable,
    ReferenceVariable,
    TupleVariable,
]


def is_valid_rvalue(v: Optional[SourceMapping]) -> bool:
    return isinstance(
        v,
        (
            StateVariable,
            LocalVariable,
            TopLevelVariable,
            TemporaryVariable,
            Constant,
            SolidityVariable,
            ReferenceVariable,
        ),
    )


def is_valid_lvalue(v: Optional[SourceMapping]) -> bool:
    return isinstance(
        v,
        (
            StateVariable,
            LocalVariable,
            TemporaryVariable,
            ReferenceVariable,
            TupleVariable,
        ),
    )
