"""
Module detecting bad PRNG due to the use of block.timestamp, now or blockhash (block.blockhash) as a source of randomness
"""

from typing import List, Tuple

from slither_core.analyses.data_dependency.data_dependency import is_dependent_ssa
from slither_core.analyses.data_dependency.data_dependency import is_dependent
from slither_core.core.cfg.node import Node
from slither_core.core.declarations import Function, Contract
from slither_core.core.declarations.solidity_variables import (
    SolidityVariable,
    SolidityFunction,
    SolidityVariableComposed,
)
from slither_core.core.variables.variable import Variable
from slither_core.detectors.abstract_detector import AbstractDetector, DetectorClassification
from slither_core.slithir.operations import BinaryType, Binary
from slither_core.slithir.operations import SolidityCall
from slither_core.slithir.operations.assignment import Assignment
from slither_core.slithir.operations.type_conversion import TypeConversion
from slither_core.utils.output import Output, AllSupportedOutput
from slither_core.core.declarations.solidity_variables import SOLIDITY_VARIABLES_COMPOSED, SOLIDITY_VARIABLES


# def collect_return_values_of_bad_PRNG_functions(f: Function) -> List:
#     """
#         Return the return-values of calls to blockhash()
#     Args:
#         f (Function)
#     Returns:
#         list(values)
#     """
#     values_returned = []
#     for n in f.nodes:
#         for ir in n.irs_ssa:
#             if (
#                 isinstance(ir, SolidityCall)
#                 and ir.function == SolidityFunction("blockhash(uint256)")
#                 and ir.lvalue
#             ):
#                 values_returned.append(ir.lvalue)
#     return values_returned


# def contains_bad_PRNG_sources(func: Function, blockhash_ret_values: List[Variable]) -> List[Node]:
#     """
#          Check if any node in function has a modulus operator and the first operand is dependent on block.timestamp, now or blockhash()
#     Returns:
#         (nodes)
#     """
#     ret = set()
#     # pylint: disable=too-many-nested-blocks
#     for node in func.nodes:
#         if node.contains_require_or_assert():
#             for var in node.variables_read:
#                 if is_dependent(var, SolidityVariableComposed("block.timestamp"), node):
#                     ret.add(node)
#                 if is_dependent(var, SolidityVariable("now"), node):
#                     ret.add(node)
#         for ir in node.irs:
#             if isinstance(ir, Binary) and BinaryType.return_bool(ir.type):
#                 for var_read in ir.read:
#                     if not isinstance(var_read, (Variable, SolidityVariable)):
#                         continue
#                     if is_dependent(var_read, SolidityVariableComposed("block.timestamp"), node):
#                         ret.add(node)
#                     if is_dependent(var_read, SolidityVariable("now"), node):
#                         ret.add(node)
#         for ir in node.irs_ssa:
#             if isinstance(ir, Binary) and ir.type == BinaryType.MODULO:
#                 var_left = ir.variable_left
#                 if not isinstance(var_left, (Variable, SolidityVariable)):
#                     continue
#                 if is_dependent_ssa(
#                     var_left, SolidityVariableComposed("block.timestamp"), node
#                 ) or is_dependent_ssa(var_left, SolidityVariable("now"), node):
#                     ret.add(node)
#                     break

#                 for ret_val in blockhash_ret_values:
#                     if is_dependent_ssa(var_left, ret_val, node):
#                         ret.add(node)
#                         break
#     return list(ret)

        
def contains_bad_PRNG_sources(func: Function) -> List[Node]:
    lvalue = [] 
    convert_value = []
    assignment_value = []
    results = []
    for node in func.nodes:
        for ir in node.irs:
            if isinstance(ir, SolidityCall):
                if ir.function == SolidityFunction('keccak256(bytes)') or ir.function == SolidityFunction('blockhash(uint256)'):
                    if any(word in str(ir.expression) for word in SOLIDITY_VARIABLES_COMPOSED.keys()):
                        lvalue.append(ir.lvalue.name)
                        results.append(ir.node)
            if isinstance(ir, TypeConversion):
                if str(ir.variable) in lvalue:
                    convert_value.append(ir.lvalue.name)
            if isinstance(ir, Binary) and ir.type == BinaryType.MODULO:
                results.append(node) 
            if isinstance(ir, Assignment):
                if str(ir.rvalue.name) in convert_value :
                    assignment_value.append(ir.lvalue.name)
            if node.contains_if() or node.contains_require_or_assert():
                for var in node.variables_read:
                    if str(var) in assignment_value:
                        results.append(ir.node)
    return results

def detect_bad_PRNG(contract: Contract) -> List[Tuple[Function, List[Node]]]:
    """
    Args:
        contract (Contract)
    Returns:
        list((Function), (list (Node)))
    """
    # blockhash_ret_values = []
    # for f in contract.functions:
    #     blockhash_ret_values += collect_return_values_of_bad_PRNG_functions(f)
    ret: List[Tuple[Function, List[Node]]] = []
    for f in contract.functions:
        bad_prng_nodes = contains_bad_PRNG_sources(f)
        if bad_prng_nodes:
            ret.append((f, bad_prng_nodes))
    return ret


class BadPRNG(AbstractDetector):
    """
    Detect weak PRNG due to a modulo operation on block.timestamp, now or blockhash
    """

    ARGUMENT = "weak-prng"
    HELP = "Weak PRNG"
    IMPACT = DetectorClassification.HIGH
    CONFIDENCE = DetectorClassification.MEDIUM

    WIKI = "https://github.com/crytic/slither/wiki/Detector-Documentation#weak-PRNG"

    WIKI_TITLE = "Weak PRNG"
    WIKI_DESCRIPTION = """
In blockchain, it is not possible to generate true randomness. 
The absence of true randomness means that the results of random number generation can be predicted, allowing for manipulation.

True randomness relies on unpredictable external factors such as atmospheric noise or user actions, but smart contracts do not have direct access to such factors, making it impossible to generate true randomness. 


This limitation is particularly important when smart contracts are used for security mechanisms like private key generation, as attackers could potentially predict the private keys and gain unauthorized access to accounts or funds.

There are two main methods for generating random numbers in blockchain:

<details> 
    <summary style='font-size: 16px;color:skyblue;'> 1. Using Randomness from the Blockchain Network Nodes </summary><br />

Blockchain networks provide certain variables in each block, such as 
   
|  |  |  |
---|---|---
`block.basefee(uint)`|`block.chainid(uint)`|`block.coinbase()`
`block.difficulty(uint)`|`block.gaslimit(uint)`|`block.number(uint)`
`block.timestamp(uint)`|`blockhash(uint)` 

   
Among these, `block.difficulty`, `blockhash`, `block.number`, and `block.timestamp` are commonly used for random number generation.


[Solidity Docs](https://docs.soliditylang.org/en/latest/units-and-global-variables.html#block-and-transaction-properties "Reference")

Randomness generated based on block data can limit the ability of typical users to predict the random numbers, but malicious miners can potentially manipulate block data to influence the generated randomness. 

Block data remains the same for a given block, meaning that generating randomness from the same block will always produce the same result.
</details>
<br />

<details> 
    <summary style='font-size: 16px;color:skyblue;'> 2. Using External Random Number Generators </summary><br />

   Blockchain oracles can be used to generate random number seeds, and off-chain data can be obtained on-chain using on-chain oracles. 
   External randomness sources, such as API data, can be fetched and used to influence contract behavior. 
   
   This can increase unpredictability compared to generating randomness using blockchain variables, but it may introduce trust issues related to the oracle's reliability.
</details>
<br />
    """

    
    WIKI_BACKGROUND = """
<details> 
    <summary style='font-size: 18px;color:pink;'> 💡 What is Randomness in Blockchain? </summary><br />
    
- Randomness in blockchain can be categorized into two types: pseudo-randomness and true randomness.
    - Pseudo-randomness is generated by deterministic algorithms, and if you know the initial seed value, it can be predicted. 
    - True randomness relies on entropy sources and generates random values that are unpredictable.

- Nodes in a blockchain network can generate pseudo-randomness using various algorithms, and this randomness is used in scenarios such as selecting lottery winners, distributing rewards, determining the rarity of NFT token items in games, and distributing loot.
- However, blockchain ensures that all nodes in the network reach the same conclusion, so if the same input is provided, the output of a contract will always be the same.   

</details>
<br />     
    """

    # region wiki_exploit_scenario
    WIKI_EXPLOIT_SCENARIO = """
```solidity
contract GuessTheRandomNumber {
    constructor() payable {}
    function guess(uint _guess) public {
        uint answer = uint(
            keccak256(abi.encodePacked(blockhash(block.number - 1), block.timestamp))
        );
 
        if (_guess == answer) {
            (bool sent, ) = msg.sender.call{value: 1 ether}("");
            require(sent, "Failed to send Ether");
        }
    }
 }
```
 
- If you are generating random numbers by combining the `blockhash` and `block.timestamp` of the previous block as a seed, this is used in a contract where users can guess a number, and if their guess matches the generated number, they win `1 ether`. 
- While it may seem like randomness has been introduced, it's important to note that it can still be manipulated. 

```solidity
contract Attack {
    receive() external payable {}

    unction attack(GuessTheRandomNumber guessTheRandomNumber) public {
        uint answer = uint(
            keccak256(abi.encodePacked(blockhash(block.number - 1), block.timestamp))
        );
 
        guessTheRandomNumber.guess(answer);
    }
 
    function getBalance() public view returns (uint) {
        return address(this).balance;
    }
 }
```    

- The attacker deploys the `Attack` contract by providing the address of the `GuessTheRandomNumber` contract. 
- In the `attack` function, the attacker replicates the guessing logic of the `GuessTheRandomNumber` contract, using the same method of combining the `blockhash` and `block.timestamp` of the previous block as a seed to generate random numbers.

- Since the `GuessTheRandomNumber` contract's `guess` function is executed in the same block, the values of `block.number` and `block.timestamp` remain unchanged within that block. 
- This allows the attacker to generate the same random number and, as a result, claim the `1 ether` prize.
"""
    # endregion wiki_exploit_scenario
    WIKI_EXAMPLES = """
1. `SmartBillions ICO (2017)`: SmartBillions was an Ethereum-based lottery platform where an attacker was able to manipulate the lottery game's results to claim prizes fraudulently.
    https://etherscan.io/address/0x5ace17f87c7391e5792a7683069a8025b83bbd85
    https://www.reddit.com/r/ethereum/comments/74d3dc/smartbillions_lottery_contract_just_got_hacked/   
     
2. `Fomo3D (2018)`: Fomo3D was an Ethereum smart contract-based game where an attacker could manipulate the game's outcome to dishonestly win prizes.
    https://etherscan.io/address/0xa62142888aba8370742be823c1782d17a0389da1
    https://medium.com/@zhongqiangc/randomness-in-smart-contracts-is-predictable-and-vulnerable-fomo3d-part-1-4d500c628191
    """

    WIKI_RECOMMENDATION = """
- It is advisable not to use `block.hash` and `block.timestamp` as sources for random number generation.
- Utilizing a `Commit-Reveal Scheme,` where participants commit values in advance and all commits are submitted before the actual values are revealed, is a good approach for generating randomness.
- Using decentralized solutions like `Chainlink VRF (Verifiable Random Function)` that leverage multiple inputs to generate random numbers is recommended.
- Employing hardware random number generators (RNG) to produce unpredictable, truly random values is a secure choice, making it difficult for attackers to predict the outcome.    
    
    """
    WIKI_DESCRIPTION_KOREAN="""
블록체인에서는 완전한 난수를 생성할 수 없습니다.
완전한 난수가 생성되지 않는다는 것은 난수 생성에 대한 결과를 예측할 수 있어 조작을 할 수 있다는 것을 의미합니다.

완전한 난수는 `atmospheric noise`나 `user action` 등 예측할 수 없는 외부 요인에 의존해야 하지만, 스마트 컨트랙트는 이러한 요인에 직접적으로 접근할 수 없어 완전한 난수를 생성할 수 없습니다.

특히나, 스마트 컨트랙트는 개인키 생성 등 보안 메커니즘을 위해 사용하는 경우도 있으나, 공격자가 개인 키를 예측하여 계정이나 자금에 무단으로 액세스할 수도 있습니다.

블록체인에서 난수를 생성하는 방법은 크게 두 가지로 나눌 수 있습니다.

<details> 
    <summary style='font-size: 16px;color:skyblue;'> 1. 블록체인 네트워크의 노드가 생성한 난수를 사용하는 방법 </summary><br />
   
블록 변수에는 

|  |  |  |
---|---|---
`block.basefee(uint)`|`block.chainid(uint)`|`block.coinbase()`
`block.difficulty(uint)`|`block.gaslimit(uint)`|`block.number(uint)`
`block.timestamp(uint)`|`blockhash(uint)` 


등이 있으며,

이 중 `block.difficulty`, `blockhash`, `block.number`, `block.timestamp`가 난수 생성에 주로 활용됩니다.

[Solidity Docs](https://docs.soliditylang.org/en/latest/units-and-global-variables.html#block-and-transaction-properties "Reference")

블록 데이터에 의해 생성되는 난수는 일반적인 사용자가 난수를 예측할 수 있는 가능성은 제한하지만, 악의적인 채굴자는 블록 데이터를 조작하여 난수를 조작할 수 있습니다.
블록 데이터는 한 블록에서 동일한 값을 갖고 있어, 같은 블록에서 난수를 생성하면 항상 동일한 결과를 얻을 수 있습니다.
</details>
<br />


<details> 
    <summary style='font-size: 16px;color:skyblue;'> 2. 외부 난수 생성기를 사용하는 방법 </summary><br />
   
블록체인 오라클에서 난수 시드를 생성할 수 있으며, 온체인 오라클을 사용해 오프체인 데이터를 온체인에서 얻을 수 있습니다.

API 데이터와 같은 외부 randomness 소스를 가져와 컨트랙트 동작에 영향을 줄 수 있어 블록체인 변수를 사용해 난수를 생성하는 것보다 예측 불가능성을 높일 수 있지만, 오라클에 대한 신뢰도 문제가 발생할 수 있습니다.

</details>
<br />

    """
    
    WIKI_BACKGROUND_KOREAN = """
<details> 
    <summary style='font-size: 18px;color:pink;'> 💡 블록체인에서 Randomness란? </summary><br />
    
- Randomness는 `pseudo-randomness`와 `true-randomness`로 구분할 수 있습니다.

    - `pseudo-randomness`는 결정론적 알고리즘에 의해 생성되며, 초기 시드 값을 알고 있다면 예측할 수 있습니다.
    
    - `true-randomness`는 엔트로피 소스에 의존하고 있어, 예측 불가능한 랜덤 값을 생성합니다.

- 블록체인 네트워크의 노드는 다양한 알고리즘을 이용해 `pseudo-randomness`를 생성할 수 있으며, 복권 당첨자 선정, 보상 분배, 게임에서 NFT 토큰 아이템의 희귀도, 전리품 분배 등의 시나리오에서 난수를 사용합니다.
- 그러나 블록체인은 네트워크의 모든 노드가 동일한 결론에 도달하도록 보장하기 때문에, 동일한 입력이 주어지면 컨트랙트의 출력은 항상 동일하다는 특징이 있습니다.

</details>
<br />      
    """
    WIKI_EXPLOIT_SCENARIO_KOREAN = """
```solidity
contract GuessTheRandomNumber {
    constructor() payable {}
    function guess(uint _guess) public {
        uint answer = uint(
            keccak256(abi.encodePacked(blockhash(block.number - 1), block.timestamp))
        );
 
        if (_guess == answer) {
            (bool sent, ) = msg.sender.call{value: 1 ether}("");
            require(sent, "Failed to send Ether");
        }
    }
 }
 ```
 
- 이전 블록의 `blockhash`와 `block.timestamp`을 난수 시드로 결합하여 업데이트 하는 방식으로 난수를 생성하고 있습니다.
- 사용자가 추측한 숫자가 생성된 숫자와 일치하면 `1 ether`를 획득하게 되는 컨트랙트이며, 무작위성이 도입된 것으로 보이지만 조작이 가능합니다.

```solidity
contract Attack {
    receive() external payable {}

    unction attack(GuessTheRandomNumber guessTheRandomNumber) public {
        uint answer = uint(
            keccak256(abi.encodePacked(blockhash(block.number - 1), block.timestamp))
        );
 
        guessTheRandomNumber.guess(answer);
    }
 
    function getBalance() public view returns (uint) {
        return address(this).balance;
    }
 }
 ```    
 
- 공격자는 `GuessTheRandomNumber` 컨트랙트의 주소를 전달해 deploy 하여 `Attack` 컨트랙트를 생성합니다.
- attack 함수에서는 GuessTheRandomNumber 컨트랙트의 guess 로직을 동일하게 구현하여, 이전 블록의 `blockhash`와 `block.timestamp`을 난수 시드로 결합하여 업데이트 하는 방식으로 난수를 생성합니다.
- `GuessTheRandomNumber` 컨트랙트의 `guess` 함수가 동일한 블록에서 실행되면 `block.number`와 `block.timestamp`는 변경되지 않기 때문에 동일한 난수를 생성할 수 있게 되어, 공격자는 `1 ether`를 획득할 수 있습니다.  
    """
    
    WIKI_EXAMPLES_KOREAN = """
1. `SmartBillions ICO (2017)`: SmartBillions는 이더리움 기반의 로또 플랫폼으로, 공격자가 로또 게임 결과를 조작하여 상금 획득할 수 있었습니다.
    https://etherscan.io/address/0x5ace17f87c7391e5792a7683069a8025b83bbd85
    https://www.reddit.com/r/ethereum/comments/74d3dc/smartbillions_lottery_contract_just_got_hacked/   
     
2. `Fomo3D (2018)`: Fomo3D는 이더리움 스마트 컨트랙트 기반의 게임으로, 공격자가 게임 결과를 조작하여 상금을 획득할 수 있었습니다.
    https://etherscan.io/address/0xa62142888aba8370742be823c1782d17a0389da1
    https://medium.com/@zhongqiangc/randomness-in-smart-contracts-is-predictable-and-vulnerable-fomo3d-part-1-4d500c628191
    """
    WIKI_RECOMMENDATION_KOREAN="""
- `block.hash`, `block.timestamp`를 난수 생성을 위한 소스로 사용하지 않는 것이 좋습니다.
- 참가자가 미리 값을 commit하고, 모든 commit이 제출된 후 실제 값이 공개되는 방식(`Commit-Reveal Schemes`)으로 난수를 생성하는 것이 좋습니다.
- 여러 입력을 활용해 난수를 생성하는 탈중앙화 솔루션인 `Chainlink VRF(Verifiable Random Function)`를 활용하는 것이 좋습니다.
- 하드웨어 난수 생성기(RNG)를 사용해 공격자가 예측할 수 없는 무작위 값 생성하는 것이 좋습니다.  
    """
    WIKI_REFERENCE="""
- https://www.slowmist.com/articles/solidity-security/Common-Vulnerabilities-in-Solidity-Randomness.html
- https://medium.com/@solidity101/100daysofsolidity-072-source-of-randomness-in-solidity-smart-contracts-ensuring-security-and-7af014bfac22
- https://dev.to/natachi/attack-vectors-in-solidity-09-bad-randomness-also-known-as-the-nothing-is-secret-attack-ca9
- https://medium.com/rektify-ai/bad-randomness-in-solidity-8b0e4a393858
    """
    
    
    def _detect(self) -> List[Output]:
        """Detect bad PRNG due to the use of block.timestamp, now or blockhash (block.blockhash) as a source of randomness"""
        results = []
        for c in self.compilation_unit.contracts_derived:
            values = detect_bad_PRNG(c)
            for func, nodes in values:
                for node in nodes:
                    info: List[AllSupportedOutput] = [func, ' uses a weak PRNG: "', node, '" \n']
                    info_kr=f"{func} 함수는 블록 변수를 이용하여 난수를 생성합니다. {node}"
                    json = self.generate_result(info, self.WIKI_DESCRIPTION, self.WIKI_BACKGROUND, self.WIKI_EXPLOIT_SCENARIO, self.WIKI_EXAMPLES, self.WIKI_RECOMMENDATION, info_kr, self.WIKI_DESCRIPTION_KOREAN, self.WIKI_BACKGROUND_KOREAN, self.WIKI_EXPLOIT_SCENARIO_KOREAN, self.WIKI_EXAMPLES_KOREAN, self.WIKI_RECOMMENDATION_KOREAN, self.WIKI_REFERENCE)

                    results.append(json)

        return results
    

