<button class='date-button'>2023-11-25</button>

# Audit Report

> 🔍 `Filename`: /Users/sikk/Desktop/Antibug/SafeDevAnalyzer/test/extcodesize.sol
---

[<button class='styled-button'>English</button>](extcodesize_en.md)
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
<summary style='font-size: 20px;'>incorrect-extcodesize</summary>
<div markdown='1'>

## Detect Results

| Detector | Impact | Confidence | Info |
|:---:|:---:|:---:|:---:|
| incorrect-extcodesize | <span style='color:skyblue'> Informational </span> | <span style='color:lightcoral'> High </span> | 함수 `Target.isContract(address)`가 컨트랙트의 크기를 확인하기 위해 `extcodesize`를 사용합니다. `extcodesize` 대신 `code.length`를 사용하세요.
 |||


<br />

## Vulnerabiltiy in code:

```solidity
line 5:     function isContract(address account) public view returns (bool) {

```
 ---

 <br />

## Background:


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
    

<br />

## Description:


특정 스마트 컨트랙트에서는 보안상의 이유로 `EOA`에서만 호출을 허용하고 다른 스마트 컨트랙트에서는 호출을 허용하지 않도록 정의되어 있습니다.
이러한 경우 함수가 컨트랙트에서 실행되는 것을 방지하려면 주소에 코드가 저장되지 않은 `msg.sender`를 요구하기 위해 `require` 문이 필요합니다.

그러나 어셈블리에 내장된 `extcodesize`를 사용하여 `EOA`인지 확인하는 로직은 공격자가 쉽게 우회할 수 있습니다.

주소의 코드 크기를 확인하는 것은 사용자가 영원히 잠길 수 있는 컨트랙트로 자금이나 토큰을 이체하는 것을 방지하는 등 사용자에게 이득을 주는 것이 목적일 때 유용합니다.
함수 호출자가 `EOA`이어야 하는 경우에는 이 방법을 사용하지 않는 것이 좋습니다.

컨트랙트를 구성하는 동안 해당 주소가 컨트랙트 주소이더라도 해당 주소에 대한 `extcodesize 0`을 반환하게 되어 컨트랙트를 우회할 수 있습니다.
    

<br />

## Recommendation:


solidity 0.8.0 버전부터 `code.length` 속성을 사용하여 컨트랙트 주소인지 확인할 수 있습니다.

```solidity
function isContract(address _addr) view returns (bool) {
  return _addr.code.length > 0;
}
```

주소가 컨트랙트 주소인지 확인하려면 `code.length` 속성을 사용하는 것이 더 안정적입니다.
    

<br />

## Exploit scenario:


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
    

<br />

## Reference:


- https://solidity-by-example.org/hacks/contract-size/
- https://ethereum.stackexchange.com/questions/15641/how-does-a-contract-find-out-if-another-address-is-a-contract
- https://consensys.github.io/smart-contract-best-practices/development-recommendations/solidity-specific/extcodesize-checks/    
    

</details>

