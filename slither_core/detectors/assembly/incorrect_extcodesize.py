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
    WIKI_DESCRIPTION = """
In certain smart contracts, for security reasons, calls are only permitted from Externally Owned Accounts (EOA) and not from other smart contracts. To prevent a function from being executed by a contract, a `require` statement is needed to ensure that `msg.sender` does not have any code stored, indicating that it is an EOA.

However, the logic of checking whether `msg.sender` is an EOA by using the built-in `extcodesize` in assembly can be easily bypassed by attackers.

Checking the code size of an address can be beneficial when the purpose is to protect users, such as preventing the transfer of funds or tokens into a contract that could become permanently locked. However, it is not advisable to use this method when it is necessary for the function caller to be an EOA.

During the construction of a contract, even if the address is a contract address, `extcodesize` will return 0 for that address, allowing the contract to be bypassed.
    """
    WIKI_BACKGROUND ="""
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

<details> 
    <summary style='font-size: 18px;color:pink;'> 💡 What is extcode? </summary><br />
    
The `extcodesize` function is one of the `Ethereum Virtual Machine (EVM)` opcodes, which returns the size of the code at a specific address in bytes. 
This function is used to determine whether the address that called a contract is an `Externally Owned Account (EOA)` or a `Contract Account (CA)`.

When a contract is being created, it does not yet have code, so the code executed by the constructor is not included in the bytecode.

In essence, if the code size at an address is `greater than zero`, then the address is a `CA`, and if it is `zero`, it is an `EOA`.

</details>
<br />
    """
    WIKI_EXPLOIT_SCENARIO="""
```solidity
pragma solidity ^0.8.13;

contract Target {
    function isContract(address account) public view returns (bool) {
        uint size;
        assembly {
            size := extcodesize(account)
        }
        return size > 0;
    }

    bool public pwned = false;

    function protected() external {
        require(!isContract(msg.sender), "no contract allowed");
        pwned = true;
    }
}
```

The `Target` contract is defined to allow calls only from Externally Owned Accounts (EOA) through a `protected` function, and not from other smart contracts.

Using `extcodesize`, if the caller is a Contract Account (CA), the `pwned` value is kept as `false`.

In the `protected` function, a `require` statement checks if `msg.sender` is an EOA, and if it is, the `pwned` value is changed to `true`.

However, the logic of using the built-in `extcodesize` in assembly to check if `msg.sender` is an EOA can be easily bypassed by attackers.

```solidity
contract Hack {
    bool public isContract;
    address public addr;

    constructor(address _target) {
        isContract = Target(_target).isContract(address(this));
        addr = address(this);
        Target(_target).protected();
    }
}
```

Attackers can bypass the security measures by implementing a logic in their constructor that calls the `isContract` and `protected` functions of the `Target` contract. 

This allows them to change the value of `pwned` to `true`.

    """
    WIKI_EXAMPLES=""
    WIKI_RECOMMENDATION = """
From Solidity version 0.8.0 onwards, you can check if an address is a contract address using the `code.length` property. 

```solidity
function isContract(address _addr) view returns (bool) {
  return _addr.code.length > 0;
}
```

It is more reliable to use the `code.length` property to determine if an address is a contract address.
    """

    WIKI_DESCRIPTION_KOREAN="""
특정 스마트 컨트랙트에서는 보안상의 이유로 `EOA`에서만 호출을 허용하고 다른 스마트 컨트랙트에서는 호출을 허용하지 않도록 정의되어 있습니다.
이러한 경우 함수가 컨트랙트에서 실행되는 것을 방지하려면 주소에 코드가 저장되지 않은 `msg.sender`를 요구하기 위해 `require` 문이 필요합니다.

그러나 어셈블리에 내장된 `extcodesize`를 사용하여 `EOA`인지 확인하는 로직은 공격자가 쉽게 우회할 수 있습니다.

주소의 코드 크기를 확인하는 것은 사용자가 영원히 잠길 수 있는 컨트랙트로 자금이나 토큰을 이체하는 것을 방지하는 등 사용자에게 이득을 주는 것이 목적일 때 유용합니다.
함수 호출자가 `EOA`이어야 하는 경우에는 이 방법을 사용하지 않는 것이 좋습니다.

컨트랙트를 구성하는 동안 해당 주소가 컨트랙트 주소이더라도 해당 주소에 대한 `extcodesize 0`을 반환하게 되어 컨트랙트를 우회할 수 있습니다.
    """
    WIKI_BACKGROUND_KOREAN="""
<details> 
    <summary style='font-size: 18px;color:pink;'> 💡 Inline Assembly란? </summary><br />
    
`inline-assembly`는 EVM에 직접적으로 상호작용하며 high-level에서 할 수 없는 수준의 control과 정밀도를 부여합니다.

구체적으로, 가스 사용량을 조정하거나, 특정 EVM 기능에 액세스할 수 있습니다.

solidity에서는 EVM bytecode로 컴파일하도록 설계된 중간 언어인 Yul을 사용하여 `inline-assembly`를 작성할 수 있습니다.

    assembly{ … }
형태로 작성합니다.

</details>
<br />   
    
<details> 
    <summary style='font-size: 18px;color:pink;'> 💡 extcodesize 란? </summary><br />
    
`extcodesize` 함수는 Ethereum의 `EVM(Ethereum Virtual Machine)` 명령어 중 하나로, 특정 주소에 배포된 스마트 컨트랙트의 코드 크기를 바이트 단위로 반환합니다.
`extcodesize` 함수는 contract를 호출한 주소가 `EOA(Externally Owned Accounts)`인지, `CA(Contract Accounts)`인지 확인하는데 사용됩니다.
컨트랙트를 생성할 때는 아직 코드가 없으므로 constructor로 실행되는 코드는 bytecode에 포함되지 않습니다.

즉, 주소의 코드 크기가 0보다 크면 해당 주소는 `CA`이며, 0이면 `EOA`입니다.

</details>
<br />   
    """
    WIKI_EXPLOIT_SCENARIO_KOREAN="""
```solidity
contract Target {
    function isContract(address account) public view returns (bool) {
        uint size;
        assembly {
            size := extcodesize(account)
        }
        return size > 0;
    }

    bool public pwned = false;

    function protected() external {
        require(!isContract(msg.sender), "no contract allowed");
        pwned = true;
    }
}
```
`Target` 컨트랙트는 `protected` 함수를 통해 `EOA`에서만 호출을 허용하고 다른 스마트 컨트랙트에서는 호출을 허용하지 않도록 정의되어 있습니다.

`extcodesize`를 통해 `CA`라면 `pwned` 값을 `false`로 유지합니다.

`protected` 함수에서 require 문을 통해 msg.sender가 EOA인지 확인하여 `msg.sender`가 `EOA`라면 `pwned` 값을 `true`로 변경합니다.

그러나 어셈블리에 내장된 `extcodesize`를 사용하여 `EOA`인지 확인하는 로직은 공격자가 쉽게 우회할 수 있습니다.

```solidity
contract Hack {
    bool public isContract;
    address public addr;

    constructor(address _target) {
        isContract = Target(_target).isContract(address(this));
        addr = address(this);
        Target(_target).protected();
    }
}
```
공격자는 constructor에 `Target` contract의 `isContract` 함수와 `protected` 함수를 호출하는 로직을 구현하여 우회할 수 있습니다.

이를 통해 `pwned`의 값을 `true`로 변경할 수 있게 됩니다. 
    """
    WIKI_EXAMPLES_KOREAN=""
    WIKI_RECOMMENDATION_KOREAN="""
solidity 0.8.0 버전부터 `code.length` 속성을 사용하여 컨트랙트 주소인지 확인할 수 있습니다.

```solidity
function isContract(address _addr) view returns (bool) {
  return _addr.code.length > 0;
}
```

주소가 컨트랙트 주소인지 확인하려면 `code.length` 속성을 사용하는 것이 더 안정적입니다.
    """

    WIKI_REFERENCE="""
- https://solidity-by-example.org/hacks/contract-size/
- https://ethereum.stackexchange.com/questions/15641/how-does-a-contract-find-out-if-another-address-is-a-contract
- https://consensys.github.io/smart-contract-best-practices/development-recommendations/solidity-specific/extcodesize-checks/    
    """


    @staticmethod
    def _contains_inline_extcodesize_use(node: Node) -> bool:
        results = []
        if node.type == NodeType.ASSEMBLY:
        #    print(node.irs)
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
                    func, " uses `extcodesize` for contract size check. Use `code.length` instead of `extcodesize`.\n"]
                # info = f"{func.canonical_name} uses `extcodesize` for contract size check. Use `code.length` instead of `extcodesize`.\n"
                info_kr = f"함수 `{func.canonical_name}`가 컨트랙트의 크기를 확인하기 위해 `extcodesize`를 사용합니다. `extcodesize` 대신 `code.length`를 사용하세요.\n"
                # sort the nodes to get deterministic results
                nodes.sort(key=lambda x: x.node_id)

                # for node in nodes:
                    # info += ["\t- ", node, "\n"]
                    # info_kr += f"{node.expression}\n"
                
                json = self.generate_result(info, self.WIKI_DESCRIPTION, self.WIKI_BACKGROUND, self.WIKI_EXPLOIT_SCENARIO, self.WIKI_EXAMPLES, self.WIKI_RECOMMENDATION, info_kr, self.WIKI_DESCRIPTION_KOREAN, self.WIKI_BACKGROUND_KOREAN, self.WIKI_EXPLOIT_SCENARIO_KOREAN, self.WIKI_EXAMPLES_KOREAN, self.WIKI_RECOMMENDATION_KOREAN, self.WIKI_REFERENCE)
                
                results.append(json)

        return results