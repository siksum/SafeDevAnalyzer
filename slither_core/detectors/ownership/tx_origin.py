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
    WIKI_DESCRIPTION = """
`tx.origin` can only track the information of the account that originally initiated the transaction.<br>
In complex transactions involving multiple contract calls, there are scenarios where it's necessary to identify the address of the `EOA`.<br>
In such cases, `tx.origin` cannot be used to identify the address of the `EOA`, preventing the implementation of granular access control based on immediate contract interactions.<br>

Additionally, using `tx.origin` for authentication is vulnerable to phishing attacks.    

<p align="center">
<img src="https://i.imgur.com/FGDediO.png" width="700" height="500">
</p>

Attackers can create malicious contracts and entice users to call these contracts. <br>
When a user interacts with a malicious contract, the attacker can capture the user's `EOA (Externally Owned Account)` address. <br>
Subsequently, if the attacker uses the user's `EOA` address to call a contract, `tx.origin` will still point to the user's address, thus mistakenly recognizing the attacker as a legitimate user.<br>
    """
    WIKI_BACKGROUND ="""
<details> 
    <summary style='font-size: 18px;color:pink;'> 💡 tx.origin and  msg.sender </summary><br />
    
`tx.origin` and `msg.sender` are global variables in Solidity, both representing the address of the caller.

`tx.origin` indicates the address of the account that originally created and transmitted the transaction to the network. <br>
Thus, `tx.origin` always represents the address of an `Externally Owned Account (EOA)`.<br>
It is useful when writing smart contracts that need to identify the original initiator of a transaction, such as in the implementation of multi-signature wallets.

`msg.sender` represents the address of the account that called the currently executing function. <br>
Therefore, `msg.sender` can be either the address of an `EOA` or a `Contract`. <br>
It is useful when writing smart contracts that need to verify the current sender of the message, such as in the implementation of access control features.

<br>

<div class='mermaid'>
flowchart LR
     id1(EOA) --> id2(Contract A) --> id3(Contract B) --> id4(Contract C)
</div>

<br>

If `EOA` calls `Contract A`, `Contract A` calls `Contract B`, and `Contract B` in turn calls `Contract C`, then within `Contract C`, `msg.sender` will be `Contract B`, and `tx.origin` will be `EOA`. <br>
While `msg.sender` and `tx.origin` might appear to represent the same account, `tx.origin` does not represent the address of the caller, but rather the address of the account that originally initiated the contract call.

</details>
<br />
    
    """
    WIKI_EXPLOIT_SCENARIO="""
```solidity
contract Wallet {
    address public owner;

    constructor() payable {
        owner = msg.sender;
    }

    function transfer(address payable _to, uint _amount) public {
        require(tx.origin == owner, "Not owner");

        (bool sent, ) = _to.call{value: _amount}("");
        require(sent, "Failed to send Ether");
    }
}
```    

Assuming that `Alice` deploys a `Wallet` contract, and a malicious user, `Bob`, deceives `Alice` into calling his `Attack` contract.

<br>

```solidity
contract Attack {
    address payable public owner;
    Wallet wallet;

    constructor(Wallet _wallet) {
        wallet = Wallet(_wallet);
        owner = payable(msg.sender);
    }

    function attack() public {
        wallet.transfer(owner, address(wallet).balance);
    }
}
```

When `Alice` calls the `attack` function of the `Attack` contract, this `Attack` contract then calls the `transfer` function of the `Wallet` contract. <br>
The `transfer` function in the `Wallet` contract performs authentication using `tx.origin`, which points to `Alice`'s address. <br>
Therefore, the `Attack` contract is recognized as an `EOA` with `Alice`'s address, allowing Bob to withdraw Ether from Alice's `Wallet` contract.<br>
 
    """

    WIKI_EXAMPLES=""
    WIKI_RECOMMENDATION = """
Using `tx.origin` limits interoperability between contracts because a contract that uses `tx.origin` cannot be safely used by another contract. <br>
Additionally, according to an answer by `Vitalik Buterin` on [ethereum stackexchange](https://ethereum.stackexchange.com/questions/196/how-do-i-make-my-dapp-serenity-proof/200#200) in July 2016, there is a possibility that `tx.origin` may be removed in future Ethereum protocol updates.<br>

It is safer to perform authentication using `msg.sender` instead of `tx.origin`, as follows.

```solidity
function transfer(address payable _to, uint256 _amount) public {
  require(msg.sender == owner);

  (bool sent, ) = _to.call.value(_amount)("");
  require(sent, "Failed to send Ether");
}
``` 
    """

    WIKI_DESCRIPTION_KOREAN="""
`tx.origin`은 처음 트랜잭션을 호출한 계정의 정보만 추적할 수 있습니다.<br>
여러 컨트랙트 호출이 포함된 복잡한 트랜잭션에서 `EOA`의 주소를 식별해야 하는 경우가 있습니다.<br>
이러한 경우, `tx.origin`을 사용하여 `EOA`의 주소를 식별할 수 없어, 즉각적인 컨트랙트 상호 작용을 기반으로 세분화된 접근 제어를 구현할 수 없습니다.<br>

또한, `tx.origin`을 사용하여 인증을 수행하는 것은 피싱 공격에 취약합니다.

<p align="center">
<img src="https://i.imgur.com/4E1EkZA.png" width="700" height="500">
</p>

공격자는 악의적인 컨트랙트를 작성하여 사용자가 해당 컨트랙트를 호출하도록 유도할 수 있습니다.<br>
사용자가 악의적인 컨트랙트과 상호 작용하면, 공격자는 사용자의 `EOA` 주소를 획득할 수 있습니다.<br>
이후, 공격자가 사용자의 `EOA` 주소를 사용하여 컨트랙트를 호출하면, `tx.origin`은 여전히 사용자의 주소를 가리키므로 공격자를 합법적인 사용자로 인식합니다.<br>
    """
    WIKI_BACKGROUND_KOREAN="""
<details> 
    <summary style='font-size: 18px;color:pink;'> 💡 tx.origin과 msg.sender </summary><br />
    
`tx.origin`과 `msg.sender`는 solidity global variable로서, 둘 다 호출자의 주소를 나타냅니다.


`tx.origin`은 트랜잭션을 처음 생성하고 네트워크에 전송한 계정의 주소를 나타냅니다.<br>
따라서 `tx.origin`은 항상 `EOA(Externally Owned Account)`의 주소를 의미합니다.<br>
다중 서명 지갑을 구현할 때와 같이 트랜잭션의 최초 발신자를 식별해야 하는 스마트 컨트랙트를 작성할 때 유용합니다.<br>

`msg.sender`는 현재 실행 중인 함수를 호출한 계정의 주소를 나타냅니다.<br>
그렇기 때문에 `msg.sender`는 `EOA`의 주소일 수도 있고, `Contract`의 주소일 수도 있습니다.<br>
접근 제어 기능을 구현할 때와 같이 메시지의 현재 발신자를 확인해야 하는 스마트 컨트랙트를 작성할 때 유용합니다.<br>

<br>

<div class='mermaid'>
flowchart LR
     id1(EOA) --> id2(Contract A) --> id3(Contract B) --> id4(Contract C)
</div>

<br>

`EOA`가 `Contract A`를 호출하고, `Contract A`가 `Contract B`를 호출하며, `Contract B`가 `Contract C`를 호출하는 경우, `Contract C`에서 `msg.sender`는 `Contract B`이고, `tx.origin`은 `EOA`입니다.<br>
`msg.sender`와 `tx.origin`은 같은 계정을 나타내는 것처럼 보이지만, `tx.origin`은 호출자의 주소를 나타내는 것이 아니라, 최초로 `Contract`를 호출한 계정의 주소를 나타냅니다.

</details>
<br />
    """
    WIKI_EXPLOIT_SCENARIO_KOREAN="""
```solidity
contract Wallet {
    address public owner;

    constructor() payable {
        owner = msg.sender;
    }

    function transfer(address payable _to, uint _amount) public {
        require(tx.origin == owner, "Not owner");

        (bool sent, ) = _to.call{value: _amount}("");
        require(sent, "Failed to send Ether");
    }
}
```

`Alice`가 `Wallet` 컨트랙트를 배포하고, 악의적인 사용자 `Bob`이 `Alice`를 속여 `Bob`의 `Attack` 컨트랙트를 호출하도록 유도한다고 가정합니다.

<br>

```solidity
contract Attack {
    address payable public owner;
    Wallet wallet;

    constructor(Wallet _wallet) {
        wallet = Wallet(_wallet);
        owner = payable(msg.sender);
    }

    function attack() public {
        wallet.transfer(owner, address(wallet).balance);
    }
}
```

`Alice`가 `Attack` 컨트랙트의 `attack` 함수를 호출하면, `Attack` 컨트랙트는 `Wallet` 컨트랙트의 `transfer` 함수를 호출합니다.<br>
`Wallet` 컨트랙트의 `transfer` 함수는 `tx.origin`을 사용하여 인증을 수행하므로, `tx.origin`은 `Alice`의 주소를 가리킵니다.<br>
따라서, `Attack` 컨트랙트는 `Alice`의 주소를 가진 `EOA`로 인식되어, Bob은 Alice의 `Wallet` 컨트랙트로부터 이더를 인출할 수 있습니다.<br>

    """
    WIKI_EXAMPLES_KOREAN=""
    WIKI_RECOMMENDATION_KOREAN="""
`tx.origin`을 사용하면 다른 컨트랙트에서 `tx.origin`을 사용하는 컨트랙트를 사용할 수 없기 때문에 컨트랙트 간의 상호 운용성이 제한됩니다.<br>
또한, 2016년 7월, `Vitalik Buterin`이 [ethereum stackexchange](https://ethereum.stackexchange.com/questions/196/how-do-i-make-my-dapp-serenity-proof/200#200)에 남긴 답변에 의하면, 향후 이더리움 프로토콜에서 tx.origin을 제거할 가능성이 있습니다.<br>

아래와 같이 `tx.origin` 대신 `msg.sender`를 사용하여 인증을 수행하는 것이 안전합니다.

```solidity
function transfer(address payable _to, uint256 _amount) public {
  require(msg.sender == owner);

  (bool sent, ) = _to.call.value(_amount)("");
  require(sent, "Failed to send Ether");
}
```
    """

    WIKI_REFERENCE="""
- https://ethereum.stackexchange.com/questions/1891/whats-the-difference-between-msg-sender-and-tx-origin
- https://docs.soliditylang.org/en/v0.8.17/security-considerations.html#tx-origin
- https://stackoverflow.com/questions/73554510/msg-sender-preferred-over-tx-origin-in-solidity
- https://consensys.github.io/smart-contract-best-practices/development-recommendations/solidity-specific/tx-origin/
- https://dev.to/zenodavids/avoiding-security-vulnerabilities-the-txorigin-vs-msgsender-debate-24an    
    """

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
                        f"`{func}`", " uses `tx.origin` for authorization: ", node, "\n"]
                    
                    info_kr= f"함수 `{func.canonical_name}`에서 `tx.origin`을 사용하여 인증을 수행합니다.\n"
                    
                    json = self.generate_result(info, self.WIKI_DESCRIPTION, self.WIKI_BACKGROUND, self.WIKI_EXPLOIT_SCENARIO, self.WIKI_EXAMPLES, self.WIKI_RECOMMENDATION, info_kr, self.WIKI_DESCRIPTION_KOREAN, self.WIKI_BACKGROUND_KOREAN, self.WIKI_EXPLOIT_SCENARIO_KOREAN, self.WIKI_EXAMPLES_KOREAN, self.WIKI_RECOMMENDATION_KOREAN, self.WIKI_REFERENCE)

                    results.append(json)

        return results
