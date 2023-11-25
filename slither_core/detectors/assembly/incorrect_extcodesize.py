"""
Module detecting usage of extcodesize in inline assembly
"""
from typing import List, Tuple

from slither_core.core.cfg.node import Node, NodeType
from slither_core.core.declarations.contract import Contract
from slither_core.core.declarations.function_contract import FunctionContract
from slither_core.detectors.abstract_detector import (
    AbstractDetector,
    DetectorClassification,
    DETECTOR_INFO,
)
from slither_core.utils.output import Output
from slither_core.core.expressions.assignment_operation import AssignmentOperation
from slither_core.core.expressions.binary_operation import BinaryOperation


class IncorrectExtcodesize(AbstractDetector):
    """
    Detect usage of extcodesize in inline assembly
    """

    ARGUMENT = "incorrect-extcodesize"
    HELP = "Incorrect extcodesize usage"
    IMPACT = DetectorClassification.INFORMATIONAL
    CONFIDENCE = DetectorClassification.HIGH

    WIKI = "https://github.com/crytic/slither/wiki/Detector-Documentation#assembly-usage"

    WIKI_TITLE = "Incorrect extcodesize usage"
    WIKI_DESCRIPTION = ""
    WIKI_BACKGROUND =""
    WIKI_EXPLOIT_SCENARIO=""
    WIKI_EXAMPLES=""
    WIKI_RECOMMENDATION = ""

    WIKI_DESCRIPTION_KOREAN=""
    WIKI_BACKGROUND_KOREAN=""
    WIKI_EXPLOIT_SCENARIO_KOREAN=""
    WIKI_EXAMPLES_KOREAN=""
    WIKI_RECOMMENDATION_KOREAN=""

    WIKI_REFERENCE=""


    @staticmethod
    def _contains_inline_extcodesize_use(node: Node) -> bool:
        results = []
        if node.type == NodeType.ASSEMBLY:
           print(node.irs)
        for ir in node.irs:
            #print(ir)
            
            if isinstance(ir.expression, AssignmentOperation) and "extcodesize" in str(ir.expression.expression_right):
                results.append(ir.expression.__str__())
            elif isinstance(ir.expression, BinaryOperation) and " > 0" in str(ir.expression):
                results.append(ir.expression.__str__())

                # results.append({"expression":ir.expression.__str__(),"operation":ir.expression.__str__()})
        return results

    def detect_assembly(self, contract: Contract) -> List[Tuple[FunctionContract, List[Node]]]:
        ret = []
        for f in contract.functions_and_modifiers:
            nodes = f.nodes
            ext_nodes = [
                n for n in nodes if self._contains_inline_extcodesize_use(n)]
            if ext_nodes:
                ret.append((f, ext_nodes))
        return ret

    def _detect(self) -> List[Output]:
        """Detect the functions that use inline assembly"""
        results = []
        for c in self.contracts:
            values = self.detect_assembly(c)
            for func, nodes in values:
                info: DETECTOR_INFO = [
                    func, " uses extcodesize for contract size check. Use extcodehash instead of extcodesize.\n"]

                # sort the nodes to get deterministic results
                nodes.sort(key=lambda x: x.node_id)

                for node in nodes:
                    info += ["\t- ", node, "\n"]
                    info_kr += f"{node.expression}, 어셈블리 사용\n"
                
                json = self.generate_result(info, self.WIKI_DESCRIPTION, self.WIKI_BACKGROUND, self.WIKI_EXPLOIT_SCENARIO, self.WIKI_EXAMPLES, self.WIKI_RECOMMENDATION, info_kr, self.WIKI_DESCRIPTION_KOREAN, self.WIKI_BACKGROUND_KOREAN, self.WIKI_EXPLOIT_SCENARIO_KOREAN, self.WIKI_EXAMPLES_KOREAN, self.WIKI_RECOMMENDATION_KOREAN, self.WIKI_REFERENCE)
                
                results.append(json)

        return results