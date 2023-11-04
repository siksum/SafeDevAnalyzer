from slither_core.core.declarations.contract_level import ContractLevel
from slither_core.core.declarations import Structure


class StructureContract(Structure, ContractLevel):
    def is_declared_by(self, contract):
        """
        Check if the element is declared by the contract
        :param contract:
        :return:
        """
        return self.contract == contract
