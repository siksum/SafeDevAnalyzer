from typing import TYPE_CHECKING
from slither_core.core.declarations.contract_level import ContractLevel


from slither_core.core.declarations.custom_error import CustomError

if TYPE_CHECKING:
    from slither_core.core.declarations import Contract


class CustomErrorContract(CustomError, ContractLevel):
    def is_declared_by(self, contract: "Contract") -> bool:
        """
        Check if the element is declared by the contract
        :param contract:
        :return:
        """
        return self.contract == contract
