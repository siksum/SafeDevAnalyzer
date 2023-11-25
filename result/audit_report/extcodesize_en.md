<button class='date-button'>2023-11-25</button>

# Audit Report

> 🔍 `Filename`: /Users/sikk/Desktop/Antibug/SafeDevAnalyzer/test/extcodesize.sol
---

[<button class='styled-button'>Korean</button>](extcodesize_kr.md)
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
| incorrect-extcodesize | <span style='color:skyblue'> Informational </span> | <span style='color:lightcoral'> High </span> | Target.isContract(address) (test/extcodesize.sol#5-14) uses `extcodesize` for contract size check. Use `code.length` instead of `extcodesize`.
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
    

<br />

## Description:


In certain smart contracts, for security reasons, calls are only permitted from Externally Owned Accounts (EOA) and not from other smart contracts. To prevent a function from being executed by a contract, a `require` statement is needed to ensure that `msg.sender` does not have any code stored, indicating that it is an EOA.

However, the logic of checking whether `msg.sender` is an EOA by using the built-in `extcodesize` in assembly can be easily bypassed by attackers.

Checking the code size of an address can be beneficial when the purpose is to protect users, such as preventing the transfer of funds or tokens into a contract that could become permanently locked. However, it is not advisable to use this method when it is necessary for the function caller to be an EOA.

During the construction of a contract, even if the address is a contract address, `extcodesize` will return 0 for that address, allowing the contract to be bypassed.
    

<br />

## Recommendation:


From Solidity version 0.8.0 onwards, you can check if an address is a contract address using the `code.length` property. 

```solidity
function isContract(address _addr) view returns (bool) {
  return _addr.code.length > 0;
}
```

It is more reliable to use the `code.length` property to determine if an address is a contract address.
    

<br />

## Exploit scenario:


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

    

<br />

## Reference:


- https://solidity-by-example.org/hacks/contract-size/
- https://ethereum.stackexchange.com/questions/15641/how-does-a-contract-find-out-if-another-address-is-a-contract
- https://consensys.github.io/smart-contract-best-practices/development-recommendations/solidity-specific/extcodesize-checks/    
    

</details>

