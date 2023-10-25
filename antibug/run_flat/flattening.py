import uuid
import os
from enum import Enum as PythonEnum
from pathlib import Path
from collections import namedtuple
from typing import List, Set, Dict, Optional, Sequence
from slither_core.core.compilation_unit import SlitherCompilationUnit
from slither_core.core.declarations import EnumContract, StructureContract
from slither_core.core.declarations.contract import Contract
from slither_core.core.declarations.function_top_level import FunctionTopLevel
from slither_core.core.declarations.top_level import TopLevel
from slither_core.core.declarations.solidity_variables import SolidityCustomRevert
from slither_core.core.solidity_types import MappingType, ArrayType
from slither_core.core.solidity_types.type import Type
from slither_core.core.solidity_types.user_defined_type import UserDefinedType
from slither_core.slithir.operations import NewContract, TypeConversion, SolidityCall, InternalCall


class Strategy(PythonEnum):
    MostDerived = 0
    OneFile = 1
    LocalImport = 2


Export = namedtuple("Export", ["filename", "content"])


def save_to_disk(files: List[Export]):
    """
    Save projects to a zip
    """
    for file in files:
        with open(file.filename, "w", encoding="utf8") as f:
            f.write(file.content)


STRATEGIES_NAMES = ",".join([i.name for i in Strategy])

DEFAULT_EXPORT_PATH = Path("crytic-export/flattening")


class Flattening:
    # pylint: disable=too-many-instance-attributes,too-many-arguments,too-many-locals,too-few-public-methods
    def __init__(
        self,
        compilation_unit: SlitherCompilationUnit,
        export_path: Optional[str] = None,
    ):
        self._source_codes: Dict[Contract, str] = {}
        self._source_codes_top_level: Dict[TopLevel, str] = {}
        self._compilation_unit: SlitherCompilationUnit = compilation_unit
        self._use_abi_encoder_v2 = False
        self._export_path: Path = DEFAULT_EXPORT_PATH if export_path is None else Path(
            export_path)
        self.createDirectory()

        self._check_abi_encoder_v2()

        for contract in compilation_unit.contracts:
            self._get_source_code(contract)

        self._get_source_code_top_level(compilation_unit.structures_top_level)
        self._get_source_code_top_level(compilation_unit.enums_top_level)
        self._get_source_code_top_level(compilation_unit.custom_errors)
        self._get_source_code_top_level(compilation_unit.variables_top_level)
        self._get_source_code_top_level(compilation_unit.functions_top_level)

    def createDirectory(self):
        try:
            if not os.path.exists(DEFAULT_EXPORT_PATH):
                os.makedirs(DEFAULT_EXPORT_PATH)
        except OSError:
            print("Error: Failed to create the directory.")

    def _get_source_code_top_level(self, elems: Sequence[TopLevel]) -> None:
        for elem in elems:
            self._source_codes_top_level[elem] = elem.source_mapping.content

    def _check_abi_encoder_v2(self):
        """
        Check if ABIEncoderV2 is required
        Set _use_abi_encorder_v2
        :return:
        """
        for p in self._compilation_unit.pragma_directives:
            if "ABIEncoderV2" or "abicoder v2" in str(p.directive):
                self._use_abi_encoder_v2 = True
                return

    def _get_source_code(
        self, contract: Contract
    ):  # pylint: disable=too-many-branches,too-many-statements
        """
        Save the source code of the contract in self._source_codes
        Patch the source code
        :param contract:
        :return:
        """
        src_mapping = contract.source_mapping
        content = self._compilation_unit.core.source_code[src_mapping.filename.absolute]
        start = src_mapping.start
        end = src_mapping.start + src_mapping.length
        content = content[start:end]
        self._source_codes[contract] = content

    def _pragmas(self) -> str:
        """
        Return the required pragmas
        :return:
        """
        ret = ""
        ret += f"pragma solidity {list(self._compilation_unit.crytic_compile.compilation_units.values())[0].compiler_version.version};\n"

        if self._use_abi_encoder_v2:
            ret += "pragma experimental ABIEncoderV2;\n"
        return ret

    def _export_from_type(
        self,
        t: Type,
        contract: Contract,
        exported: Set[str],
        list_contract: Set[Contract],
        list_top_level: Set[TopLevel],
    ):
        if isinstance(t, UserDefinedType):
            t_type = t.type
            if isinstance(t_type, TopLevel):
                list_top_level.add(t_type)
            elif isinstance(t_type, (EnumContract, StructureContract)):
                if t_type.contract != contract and t_type.contract not in exported:
                    self._export_list_used_contracts(
                        t_type.contract, exported, list_contract, list_top_level
                    )
            else:
                assert isinstance(t.type, Contract)
                if t.type != contract and t.type not in exported:
                    self._export_list_used_contracts(
                        t.type, exported, list_contract, list_top_level
                    )
        elif isinstance(t, MappingType):
            self._export_from_type(t.type_from, contract,
                                   exported, list_contract, list_top_level)
            self._export_from_type(t.type_to, contract,
                                   exported, list_contract, list_top_level)
        elif isinstance(t, ArrayType):
            self._export_from_type(
                t.type, contract, exported, list_contract, list_top_level)

    def _export_list_used_contracts(  # pylint: disable=too-many-branches
        self,
        contract: Contract,
        exported: Set[str],
        list_contract: Set[Contract],
        list_top_level: Set[TopLevel],
    ):
        # TODO: investigate why this happen
        if not isinstance(contract, Contract):
            return
        if contract.name in exported:
            return
        exported.add(contract.name)
        for inherited in contract.inheritance:
            self._export_list_used_contracts(
                inherited, exported, list_contract, list_top_level)

        # Find all the external contracts called
        externals = contract.all_library_calls + contract.all_high_level_calls
        # externals is a list of (contract, function)
        # We also filter call to itself to avoid infilite loop
        externals = list({e[0] for e in externals if e[0] != contract})

        for inherited in externals:
            self._export_list_used_contracts(
                inherited, exported, list_contract, list_top_level)

        for list_libs in contract.using_for.values():
            for lib_candidate_type in list_libs:
                if isinstance(lib_candidate_type, UserDefinedType):
                    lib_candidate = lib_candidate_type.type
                    if isinstance(lib_candidate, Contract):
                        self._export_list_used_contracts(
                            lib_candidate, exported, list_contract, list_top_level
                        )

        # Find all the external contracts use as a base type
        local_vars = []
        for f in contract.functions_declared:
            local_vars += f.variables

        for v in contract.variables + local_vars:
            self._export_from_type(
                v.type, contract, exported, list_contract, list_top_level)

        for s in contract.structures:
            for elem in s.elems.values():
                self._export_from_type(
                    elem.type, contract, exported, list_contract, list_top_level)

        # Find all convert and "new" operation that can lead to use an external contract
        for f in contract.functions_declared:
            for ir in f.slithir_operations:
                if isinstance(ir, NewContract):
                    if ir.contract_created != contract and not ir.contract_created in exported:
                        self._export_list_used_contracts(
                            ir.contract_created, exported, list_contract, list_top_level
                        )
                if isinstance(ir, TypeConversion):
                    self._export_from_type(
                        ir.type, contract, exported, list_contract, list_top_level
                    )

                for read in ir.read:
                    if isinstance(read, TopLevel):
                        list_top_level.add(read)
                if isinstance(ir, InternalCall) and isinstance(ir.function, FunctionTopLevel):
                    list_top_level.add(ir.function)
                if (
                    isinstance(ir, SolidityCall)
                    and isinstance(ir.function, SolidityCustomRevert)
                    and isinstance(ir.function.custom_error, TopLevel)
                ):
                    list_top_level.add(ir.function.custom_error)

        list_contract.add(contract)

    def _export_contract_with_inheritance(self, contract) -> Export:
        list_contracts: Set[Contract] = set()  # will contain contract itself
        list_top_level: Set[TopLevel] = set()
        self._export_list_used_contracts(
            contract, set(), list_contracts, list_top_level)
        path = Path(self._export_path, f"{contract.name}_{uuid.uuid4()}.sol")

        content = "// SPDX-License-Identifier: UNLICENSED\n"
        content += self._pragmas()

        for listed_top_level in list_top_level:
            content += self._source_codes_top_level[listed_top_level]
            content += "\n"

        for listed_contract in list_contracts:
            content += self._source_codes[listed_contract]
            content += "\n"

        return Export(filename=path, content=content)

    def _export_most_derived(self) -> List[Export]:
        ret: List[Export] = []
        for contract in self._compilation_unit.contracts_derived:
            ret.append(self._export_contract_with_inheritance(contract))
        return ret

    def _export_all(self) -> List[Export]:
        # path = Path(self._export_path, "export1.sol")

        current_directory = Path.cwd()
        contract_name = str(self._compilation_unit.contracts[0])
        path = current_directory / f"flat_{contract_name}.sol"

        content = "// SPDX-License-Identifier: UNLICENSED\n"
        content += self._pragmas()

        for top_level_content in self._source_codes_top_level.values():
            content += "\n"
            content += top_level_content
            content += "\n"

        contract_seen = set()
        contract_to_explore = list(self._compilation_unit.contracts)

        # We only need the inheritance order here, as solc can compile
        # a contract that use another contract type (ex: state variable) that he has not seen yet
        while contract_to_explore:
            next_to_explore = contract_to_explore.pop(0)

            if not next_to_explore.inheritance or all(
                (father in contract_seen for father in next_to_explore.inheritance)
            ):
                content += "\n"
                content += self._source_codes[next_to_explore]
                content += "\n"
                contract_seen.add(next_to_explore)
            else:
                contract_to_explore.append(next_to_explore)

        return [Export(filename=path, content=content)]

    def export(  # pylint: disable=too-many-arguments,too-few-public-methods
        self,
        strategy: Strategy,
    ):
        exports: List[Export] = []
        if strategy == Strategy.MostDerived:
            exports = self._export_most_derived()
        elif strategy == Strategy.OneFile:
            exports = self._export_all()

        save_to_disk(exports)
