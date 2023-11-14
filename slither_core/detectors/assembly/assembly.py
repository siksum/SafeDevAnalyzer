"""
Module detecting usage of inline assembly
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


class Assembly(AbstractDetector):
    """
    Detect usage of inline assembly
    """

    ARGUMENT = "assembly"
    HELP = "Assembly usage"
    IMPACT = DetectorClassification.INFORMATIONAL
    CONFIDENCE = DetectorClassification.LOW

    WIKI = "https://github.com/crytic/slither/wiki/Detector-Documentation#assembly-usage"

    WIKI_TITLE = "Assembly usage"
    WIKI_DESCRIPTION = """
<details> 
    <summary style='font-size: 18px;color:pink;'> 💡 What is Inline Assembly? </summary><br />
    
`inline-assembly` allows for direct interaction with the EVM, providing a level of control and precision that is not achievable at a high-level.

Specifically, it enables you to adjust gas usage and access specific EVM features. In Solidity, you can write `inline-assembly` using the intermediate language Yul, which is designed to compile into EVM bytecode. 

It is written in the following form:

```solidity
assembly{ ... }
```

</details>
<br />

Typically, the Solidity compiler performs checks to ensure that memory is well-defined and safe. However, when using `inline-assembly`, you can bypass the compiler's checks, potentially leading to memory manipulation.
"""

    WIKI_EXPLOIT_SCENARIO = """
```solidity
contract VulnerableContract {
    uint8 public balance;

    function deposit(uint8 amount) public {
        assembly {
            sstore(balance.slot, add(sload(balance.slot), amount))
        }
    }

    function withdraw(uint8 amount) public {
        require(amount <= balance, "Insufficient balance");
        assembly {
            sstore(balance.slot, sub(sload(balance.slot), amount))
        }
    }
}
```


In the `deposit` function, the `add` assembly instruction is used to add `amount` to the `balance`. 
If the `balance` is close to its maximum value, such as 255, an overflow can occur when attempting to add more, causing the `balance` to wrap around unexpectedly and decrease.
"""
    WIKI_RECOMMENDATION = "Be cautious when using `inline assembly.`"
    WIKI_DESCRIPTION_KOREAN="""
<details> 
    <summary style='font-size: 18px;color:pink;'> 💡 Inline Assembly란? </summary><br />
    
`inline-assembly`는 EVM에 직접적으로 상호작용하며 high-level에서 할 수 없는 수준의 control과 정밀도를 부여합니다.

구체적으로, 가스 사용량을 조정하거나, 특정 EVM 기능에 액세스할 수 있습니다.

solidity에서는 EVM bytecode로 컴파일하도록 설계된 중간 언어인 Yul을 사용하여 `inline-assembly`를 작성할 수 있습니다.

    assembly{ … }
형태로 작성합니다.

</details>
<br />

일반적으로 solidity 컴파일러는 메모리가 잘 정의되어 있는지 확인하고 있지만, `inline-assembly`를 사용하면 컴파일러의 검사를 벗어나기 때문에 메모리 조작으로 이어질 수 있습니다.
    
"""
    WIKI_EXPLOIT_SCENARIO_KOREAN = """
```solidity
contract VulnerableContract {
    uint8 public balance;

    function deposit(uint8 amount) public {
        assembly {
            sstore(balance.slot, add(sload(balance.slot), amount))
        }
    }

    function withdraw(uint8 amount) public {
        require(amount <= balance, "Insufficient balance");
        assembly {
            sstore(balance.slot, sub(sload(balance.slot), amount))
        }
    }
}
```    
`deposit` 함수에서 `amount`를 `balance`에 더할 때 `add` 명령을 사용하고 있습니다.
`balance`가 최댓값이 255에 가까워진 상태에서 더하려고 하면 오버플로우가 발생하여 `balance`가 감소할 수 있습니다.
"""
    WIKI_RECOMMENDATION_KOREAN="`inline assembly` 사용에 주의하세요."
    WIKI_REFERENCE="""
- https://medium.com/@ac1d_eth/technical-exploration-of-inline-assembly-in-solidity-b7d2b0b2bda8
- [https://solidity-kr.readthedocs.io/ko/latest/assembly.html#:~:text=Inline assembly is a way to access the Ethereum Virtual Machine at a low level. This bypasses several important safety features and checks of Solidity. You should only use it for tasks that need it%2C and only if you are confident with using it](https://solidity-kr.readthedocs.io/ko/latest/assembly.html#:~:text=Inline%20assembly%20is%20a%20way%20to%20access%20the%20Ethereum%20Virtual%20Machine%20at%20a%20low%20level.%20This%20bypasses%20several%20important%20safety%20features%20and%20checks%20of%20Solidity.%20You%20should%20only%20use%20it%20for%20tasks%20that%20need%20it%2C%20and%20only%20if%20you%20are%20confident%20with%20using%20it).    
    """
    
    @staticmethod
    def _contains_inline_assembly_use(node: Node) -> bool:
        """
             Check if the node contains ASSEMBLY type
        Returns:
            (bool)
        """
        return node.type == NodeType.ASSEMBLY

    def detect_assembly(self, contract: Contract) -> List[Tuple[FunctionContract, List[Node]]]:
        ret = []
        for f in contract.functions:
            if f.contract_declarer != contract:
                continue
            nodes = f.nodes
            assembly_nodes = [n for n in nodes if self._contains_inline_assembly_use(n)]
            if assembly_nodes:
                ret.append((f, assembly_nodes))
        return ret

    def _detect(self) -> List[Output]:
        """Detect the functions that use inline assembly"""
        results = []
        for c in self.contracts:
            values = self.detect_assembly(c)
            for func, nodes in values:
                info: DETECTOR_INFO = ["Function ", func, " uses inline-assembly\n"]
                info_kr = f"함수 `{func.canonical_name}`에서 `inline-assembly`가 사용되었습니다.\n"
                # sort the nodes to get deterministic results
                # nodes.sort(key=lambda x: x.node_id)

                # for node in nodes:
                #     info += ["\t- ", node, "\n"]
                #     info_kr += f"{node.expression}, 어셈블리 사용\n"

                json = self.generate_result(info, self.WIKI_DESCRIPTION, self.WIKI_EXPLOIT_SCENARIO, self.WIKI_RECOMMENDATION, info_kr, self.WIKI_DESCRIPTION_KOREAN, self.WIKI_EXPLOIT_SCENARIO_KOREAN, self.WIKI_RECOMMENDATION_KOREAN, self.WIKI_REFERENCE)

                results.append(json)

        return results
