from typing import List
from slither_core.detectors.abstract_detector import (
    AbstractDetector,
    DetectorClassification,
    DETECTOR_INFO,
)
from slither_core.slithir.operations import Binary, BinaryType
from slither_core.slithir.variables import Constant
from slither_core.core.declarations.function_contract import FunctionContract
from slither_core.utils.output import Output


class ShiftParameterMixup(AbstractDetector):
    """
    Check for cases where a return(a,b) is used in an assembly function that also returns two variables
    """

    ARGUMENT = "incorrect-shift"
    HELP = "The order of parameters in a shift instruction is incorrect."
    IMPACT = DetectorClassification.HIGH
    CONFIDENCE = DetectorClassification.HIGH

    WIKI = (
        "https://github.com/crytic/slither/wiki/Detector-Documentation#incorrect-shift-in-assembly"
    )

    WIKI_TITLE = "Incorrect shift in assembly."
    WIKI_DESCRIPTION = "When using shift operations in an assembly function, it is important to check for cases where the parameters are in the wrong order."

    # region wiki_exploit_scenario
    WIKI_EXPLOIT_SCENARIO = """
```solidity
contract C {
    function f() internal returns (uint a) {
        assembly {
            a := shr(a, 8)
        }
    }
}
```
`shr(a, 8)`: Shifts the bits of variable 'a' 8 positions to the right. In other words, it moves the value of 'a' 8 bits to the right.
`shr(8, a)`: Shifts the number 8 to the right by the number of bits in variable 'a'. This safely shifts 'a' to the right by 8 bits, regardless of its value.

`shl(a, 8)`: The variable a is being shifted. The result can vary depending on the value and bit length of a. If a has a sufficiently large value such that left-shifting it would exceed the bit length, unexpected values may occur.
`shl(8, a)`: The number 8 is a fixed value being used to perform the shift operation. Therefore, the result of the shift operation depends solely on the value of the variable a. Consequently, it's safe to perform an 8-bit left shift on a, regardless of its current value.
"""
    # endregion wiki_exploit_scenario

    WIKI_RECOMMENDATION = """
In general, `shl(8, a)` and `shr(8, a)` can be more predictable and safer approaches. However, the choice of method may vary depending on the specific circumstances and the data being used. The decision should be made carefully, taking into account the requirements and goals of the program.
Furthermore, Solidity Yul code does not check for Overflow/Underflow, so you should write your code with these cases in mind and handle them appropriately.
"""
    
    WIKI_DESCRIPTION_KOREAN="""
어셈블리 함수에서 shift 연산을 사용할 때, 파라미터의 순서가 잘못된 경우를 검사합니다.
    """
    
    WIKI_EXPLOIT_SCENARIO_KOREAN="""
```solidity
contract C {
    function f() internal returns (uint a) {
        assembly {
            a := shr(a, 8)
        }
    }
}
```
`shr(a, 8)`: 변수 a의 비트를 오른쪽으로 8개만큼 시프트합니다. 즉, a의 값을 8비트 오른쪽으로 이동시킵니다.
`shr(8, a)`: 숫자 8을 변수 a의 비트 수만큼 오른쪽으로 시프트합니다. 따라서 a 변수가 어떤 값이든 안전하게 8 비트만큼 오른쪽으로 시프트됩니다.
    
`shl(a, 8)`: a 변수가 시프트됩니다. a 변수의 값과 비트 길이에 따라 결과가 달라질 수 있습니다. 만약 a가 충분히 큰 값을 갖고 있어서 왼쪽 시프트로 인해 비트 길이가 넘어가는 경우, 예상치 못한 값이 발생할 수 있습니다.
`shl(8, a)`: 8이 고정된 값을 시프트하는 것이므로 시프트 연산의 결과는 a 변수의 값에만 의존합니다. 따라서 a 변수가 어떤 값이든 안전하게 8 비트만큼 왼쪽으로 시프트됩니다.
"""

    WIKI_RECOMMENDATION_KOREAN="""
보통은 `shl(8, a)`, `shr(8, a)`가 더 예측 가능하고 안전한 방법일 수 있습니다. 하지만 실제 상황과 사용하는 데이터에 따라서 다른 방식이 더 적합할 수 있습니다. 이러한 결정은 프로그램의 요구 사항과 목적에 따라 다르므로 주의 깊게 검토하고 적절한 방법을 선택해야 합니다.
또한, solidity yul code는 Overflow/Underflow를 검사하지 않으므로, 이러한 케이스를 고려하여 코드를 작성해야 합니다.
    """
    WIKI_REFERENCE="""
- https://ethereum.stackexchange.com/questions/127538/right-shift-not-working-in-inline-assembly
- https://docs.soliditylang.org/en/v0.8.23/types.html#value-types:~:text=Before%20version%200.5.0%20a%20right%20shift%20x%20%3E%3E%20y%20for%20negative%20x%20was%20equivalent%20to%20the%20mathematical%20expression%20x%20/%202**y%20rounded%20towards%20zero%2C%20i.e.%2C%20right%20shifts%20used%20rounding%20up%20(towards%20zero)%20instead%20of%20rounding%20down%20(towards%20negative%20infinity).
- https://docs.soliditylang.org/en/v0.8.23/types.html#value-types:~:text=Overflow%20checks%20are%20never%20performed%20for%20shift%20operations%20as%20they%20are%20done%20for%20arithmetic%20operations.%20Instead%2C%20the%20result%20is%20always%20truncated.    
    """
    

    def _check_function(self, f: FunctionContract) -> List[Output]:
        results = []

        for node in f.nodes:
            for ir in node.irs:
                if isinstance(ir, Binary) and ir.type in [
                    BinaryType.LEFT_SHIFT,
                    BinaryType.RIGHT_SHIFT,
                ]:
                    if isinstance(ir.variable_left, Constant) and not isinstance(
                        ir.variable_right, Constant
                    ):
                        info: DETECTOR_INFO = [
                            f,
                            " contains an incorrect shift operation: ",
                            node,
                            "\n",
                        ]
                        info_kr=f"{f} 함수는 잘못된 shift 연산을 포함하고 있습니다. {node}"
                        json = self.generate_result(info, self.WIKI_DESCRIPTION, self.WIKI_EXPLOIT_SCENARIO, self.WIKI_RECOMMENDATION, info_kr, self.WIKI_DESCRIPTION_KOREAN, self.WIKI_EXPLOIT_SCENARIO_KOREAN, self.WIKI_RECOMMENDATION_KOREAN, self.WIKI_REFERENCE)
                        results.append(json)
        return results

    def _detect(self) -> List[Output]:
        results = []
        for c in self.contracts:
            for f in c.functions:
                if f.contract_declarer != c:
                    continue

                if f.contains_assembly:
                    results += self._check_function(f)
                    
        return results
