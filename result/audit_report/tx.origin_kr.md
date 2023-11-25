<button class='date-button'>2023-11-25</button>

# Audit Report

> 🔍 `Filename`: /Users/sikk/Desktop/Antibug/SafeDevAnalyzer/test/tx.origin.sol
---

[<button class='styled-button'>English</button>](tx.origin_en.md)
<br />


<style>
    .date-button{
        color:black;
        border:none;
        font-weight: bold;
        background-color: sand;
        width: 150px;
        height: 25px;
        float: right;
        border-radius: 20px;
    }
    .styled-button{
        color: black;
        border: none;
        font-weight: bold;
        background-color: lightskyblue;
        width: 100px;
        height: 30px;
        float: right;
        border-radius: 20px;
    }
    .styled-button:hover{
        color: black;
        border: none;
        font-weight: bold;
        background-color: pink;
        width: 100px;
        height: 30px;
        float: right;
        cursor: pointer;
    }
</style>

               
<details>
<summary style='font-size: 20px;'>tx-origin</summary>
<div markdown='1'>

## Detect Results

| Detector | Impact | Confidence | Info |
|:---:|:---:|:---:|:---:|
| tx-origin | <span style='color:olivedrab'> Medium </span> | <span style='color:olivedrab'> Medium </span> | 함수 `Wallet.transfer(address,uint256)`에서 `tx.origin`을 사용하여 인증을 수행합니다.
 |||


<br />

## Vulnerabiltiy in code:

```solidity
line 31:         require(tx.origin == owner, "Not owner");

```
 ---

 <br />

## Background:


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
    

<br />

## Description:


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
    

<br />

## Recommendation:


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
    

<br />

## Exploit scenario:


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

    

<br />

## Reference:


- https://ethereum.stackexchange.com/questions/1891/whats-the-difference-between-msg-sender-and-tx-origin
- https://docs.soliditylang.org/en/v0.8.17/security-considerations.html#tx-origin
- https://stackoverflow.com/questions/73554510/msg-sender-preferred-over-tx-origin-in-solidity
- https://consensys.github.io/smart-contract-best-practices/development-recommendations/solidity-specific/tx-origin/
- https://dev.to/zenodavids/avoiding-security-vulnerabilities-the-txorigin-vs-msgsender-debate-24an    
    

</details>

