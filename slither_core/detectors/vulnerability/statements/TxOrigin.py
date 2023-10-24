"""
Module detecting usage of `tx.origin` in a conditional node
"""
from typing import List, Tuple
import re

from slither_core.core.cfg.node import Node
from slither_core.core.declarations.contract import Contract
from slither_core.core.declarations.function_contract import FunctionContract
from slither_core.detectors.abstract_detector import (
    AbstractDetector,
    DetectorClassification,
    DETECTOR_INFO,
)
from slither_core.utils.output import Output


class TxOrigin(AbstractDetector):
    """
    Detect usage of tx.origin in a conditional node
    """

    ARGUMENT = "tx-origin"
    HELP = "Dangerous usage of `tx.origin`"
    IMPACT = DetectorClassification.MEDIUM
    CONFIDENCE = DetectorClassification.MEDIUM

    WIKI = (
        "https://github.com/crytic/slither/wiki/Detector-Documentation#dangerous-usage-of-txorigin"
    )

    WIKI_TITLE = "Dangerous usage of `tx.origin`"
    WIKI_DESCRIPTION = "`tx.origin`-based protection can be abused by a malicious contract if a legitimate user interacts with the malicious contract."

    # region wiki_exploit_scenario
    WIKI_EXPLOIT_SCENARIO = """
```solidity
contract TxOrigin {
    address owner = msg.sender;

    function bug() {
        require(tx.origin == owner);
    }
```
Bob is the owner of `TxOrigin`. Bob calls Eve's contract. Eve's contract calls `TxOrigin` and bypasses the `tx.origin` protection."""
    # endregion wiki_exploit_scenario

    WIKI_RECOMMENDATION = "Do not use `tx.origin` for authorization."

    @staticmethod
    def _contains_incorrect_tx_origin_use(node: Node) -> bool:
        """
             Check if the node reads tx.origin and doesn't read msg.sender
             Avoid the FP due to (msg.sender == tx.origin)
        Returns:
            (bool)
        """
        solidity_var_read = node.solidity_variables_read
        if solidity_var_read:
            return (any(v.name == "tx.origin" for v in solidity_var_read) and all(
                v.name != "msg.sender" for v in solidity_var_read) or any(v.name == "tx.origin" for v in solidity_var_read) and any(
                v.name != "msg.sender" for v in solidity_var_read))
        return False

    def detect_tx_origin(self, contract: Contract) -> List[Tuple[FunctionContract, List[Node]]]:
        ret = []
        for f in contract.functions_and_modifiers:

            nodes = f.nodes
            condtional_nodes = [
                n for n in nodes if n.contains_if() or n.contains_require_or_assert()
            ]
            bad_tx_nodes = [
                n for n in condtional_nodes if self._contains_incorrect_tx_origin_use(n)
            ]
            incorrect_tx_origin_use = [
                n for n in nodes if self.detect_tx_origin_in_funtion(n)]
            if bad_tx_nodes:
                ret.append((f, bad_tx_nodes))
            elif incorrect_tx_origin_use:
                ret.append((f, incorrect_tx_origin_use))
    
            # if bad_tx_nodes or incorrect_tx_origin_use:
            #     ret.append((f, bad_tx_nodes, incorrect_tx_origin_use))
        return ret

    def detect_tx_origin_in_funtion(self, node: Node) -> bool:
        pattern = r'tx\.origin'
        matches = []
        for ir in node.irs:
            matches.append(re.findall(
                pattern, ir.node.expression.__str__()))
        return self.isTrue(matches)

    def isTrue(self,matches):
        for match in matches:
            if match:
                return(True)    
        return(False)

    def _detect(self) -> List[Output]:
        """Detect the functions that use tx.origin in a conditional node"""
        results = []
        for c in self.contracts:
            values = self.detect_tx_origin(c)
            for func, nodes in values:
                for node in nodes:
                    info: DETECTOR_INFO = [
                        func, " uses tx.origin for authorization: ", node, "\n"]
                    res = self.generate_result(info)
                    results.append(res)

        return results
