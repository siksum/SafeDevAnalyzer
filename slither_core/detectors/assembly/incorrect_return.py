from typing import List, Optional

from slither_core.core.declarations import SolidityFunction, Function
from slither_core.detectors.abstract_detector import (
    AbstractDetector,
    DetectorClassification,
    DETECTOR_INFO,
)
from slither_core.slithir.operations import SolidityCall
from slither_core.utils.output import Output


def _assembly_node(function: Function) -> Optional[SolidityCall]:
    """
    Check if there is a node that use return in assembly

    Args:
        function:

    Returns:

    """

    for ir in function.all_slithir_operations():
        if isinstance(ir, SolidityCall) and ir.function == SolidityFunction(
            "return(uint256,uint256)"
        ):
            return ir
    return None


class IncorrectReturn(AbstractDetector):
    """
    Check for cases where a return(a,b) is used in an assembly function
    """

    ARGUMENT = "incorrect-return"
    HELP = "If a `return` is incorrectly used in assembly mode."
    IMPACT = DetectorClassification.HIGH
    CONFIDENCE = DetectorClassification.MEDIUM

    WIKI = "https://github.com/crytic/slither/wiki/Detector-Documentation#incorrect-assembly-return"

    WIKI_TITLE = "Incorrect return in assembly"
    WIKI_DESCRIPTION = "Detect if `return` in an assembly block halts unexpectedly the execution."
    WIKI_EXPLOIT_SCENARIO = """
```solidity
contract C {
    function f() internal returns (uint a, uint b) {
        assembly {
            return (5, 6)
        }
    }

    function g() returns (bool){
        f();
        return true;
    }
}
```
The return statement in `f` will cause execution in `g` to halt.
The function will return 6 bytes starting from offset 5, instead of returning a boolean."""

    WIKI_RECOMMENDATION = "Use the `leave` statement."

    WIKI_DESCRIPTION_KOREAN = "inline assembly block에 return이 사용되어 예기치 않은 실행 흐름이 중단될 수 있습니다."
    WIKI_EXPLOIT_SCENARIO_KOREAN = """
        ```solidity
            contract C {
                function f() internal returns (uint a, uint b) {
                    assembly {
                        return (5, 6)
                    }
                }

                function g() returns (bool){
                    f();
                    return true;
                }
            }
        ```
    f 함수의 return 문은 g 함수의 실행을 중단시킵니다.
    g 함수를 호출하여 true 값을 반환할 것을 기대했으나 f 함수에서 5번째 offset부터 6바이트를 반환한 뒤 실행이 중단됩니다."""

    WIKI_RECOMMENDATION_KOREAN = "0.6.0 이상 버전부터 leave 키워드가 등장하였습니다. 만약 이전 버전을 사용한다면, 0.6.0 이상 버전으로 변경한 후, solidity의 leave 문을 사용하세요."
    WIKI_REFERENCE ="https://blog.ethereum.org/2019/12/03/ef-supported-teams-research-and-development-update-2019-pt-2#solidity-060:~:text=Add%20%22leave%22%20statement%20to%20Yul%20/%20Inline%20Assembly%20to%20return%20from%20current%20function"
        
    # pylint: disable=too-many-nested-blocks
    def _detect(self) -> List[Output]:
        results: List[Output] = []
        for c in self.contracts:
            for f in c.functions_and_modifiers_declared:

                for node in f.nodes:
                    if node.sons:
                        for function_called in node.internal_calls:
                            if isinstance(function_called, Function):
                                found = _assembly_node(function_called)
                                if found:

                                    info: DETECTOR_INFO = [
                                        f,
                                        " calls ",
                                        function_called,
                                        " which halt the execution ",
                                        found.node,
                                        "\n",
                                    ]
                                    json = self.generate_result(info, self.WIKI_EXPLOIT_SCENARIO, self.WIKI_RECOMMENDATION, self.WIKI_DESCRIPTION_KOREAN, self.WIKI_EXPLOIT_SCENARIO_KOREAN, self.WIKI_RECOMMENDATION_KOREAN, self.WIKI_REFERENCE)

                                    results.append(json)

        return results
