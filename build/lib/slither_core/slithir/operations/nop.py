from typing import List


from slither_core.core.variables.variable import Variable
from slither_core.slithir.operations import Operation


class Nop(Operation):
    @property
    def read(self) -> List[Variable]:
        return []

    @property
    def used(self):
        return []

    def __str__(self):
        return "NOP"
