"""
Module detecting over/underflow
"""
from typing import List, Tuple

from slither_core.core.cfg.node import Node
from slither_core.core.declarations.contract import Contract
from slither_core.core.declarations.function_contract import FunctionContract
from slither_core.detectors.abstract_detector import (
    AbstractDetector,
    DetectorClassification,
    DETECTOR_INFO,
)
from slither_core.slithir.operations.binary import Binary
from slither_core.utils.output import Output
from antibug.compile.parse_version_and_install_solc import SolcParser 

class ArithmeticUnderOverFlow(AbstractDetector):
    """
    Detect overflow/underflow
    """

    ARGUMENT = "over-underflow"
    HELP = "If you don't use SafeMath under version 0.8.0, it can result in over/underflow."
    IMPACT = DetectorClassification.LOW
    CONFIDENCE = DetectorClassification.LOW

    WIKI = (
        "https://github.com/crytic/slither/wiki/Detector-Documentation#dangerous-usage-of-txorigin"
    )

    WIKI_TITLE = "overflow/underflow"
    WIKI_DESCRIPTION = "If you don't use SafeMath under version 0.8.0, it can result in over/underflow."

    # region wiki_exploit_scenario
    WIKI_EXPLOIT_SCENARIO = """ """
    # endregion wiki_exploit_scenario

    WIKI_RECOMMENDATION = "use SafeMath or use version 0.8.0 or higher"

    SAFEMATH_CONST = ["add", "mul", "sub", "div"]
    CONST = ["+", "-", "*"]

    @staticmethod
    def get_versions(file):
        instance = SolcParser(file)
        sign, version = instance.parse_version_in_file_contents()
        return sign, version

    def detect_over_underflow(self, contract: Contract) -> List[Tuple[FunctionContract, List[Node]]]:
        results = []
        file_path = list(self.compilation_unit.scopes.keys())[0].absolute
        (_, version) = self.get_versions(file_path)
        if any("0.8" in ver for ver in version):
            for safemath in contract.all_library_calls or []:
                if safemath[1].name in self.SAFEMATH_CONST and safemath[0].name == "SafeMath":
                    results.append(
                        {"lib": safemath[0].name, "contract": contract.name, "function": safemath[1].name})
        else:
            for function in contract.functions:
                for node in function.nodes:
                    for operation in node.all_slithir_operations():
                        if isinstance(operation, Binary):
                            result = any(c in self.CONST for c in str(
                                operation)) or 'unit' in str(operation.lvalue.type)
                            if result is True:
                                results.append(
                                    {"contract": contract.name, "func": function.name, "node": node.__str__(), "ir": operation.__str__()})

        return results

    def _detect(self) -> List[Output]:
        """Detect the overflow/underflow"""
        results = []
        for c in self.contracts:
            values = self.detect_over_underflow(c)
            for value in values:
                if 'lib' in value.keys():
                    info: DETECTOR_INFO = [
                        "You don't need to use SafeMath: ", value['contract'], ".", value['function'], "\n"]
                    res = self.generate_result(info)
                    results.append(res)
                elif 'func' in value.keys():
                    info: DETECTOR_INFO = ["In ", value["contract"], ".", value["func"],
                                           ", it can be over/underflowed. check your logic: ", value['node'], "\n"]
                    res = self.generate_result(info)
                    results.append(res)
        return results
