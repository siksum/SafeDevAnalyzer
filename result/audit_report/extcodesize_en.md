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
<summary style='font-size: 20px;'>assembly</summary>
<div markdown='1'>

## Detect Results

| Detector | Impact | Confidence | Info |
|:---:|:---:|:---:|:---:|
| assembly | <span style='color:skyblue'> Informational </span> | <span style='color:sandybrown'> Low </span> | Function Target.isContract(address) (test/extcodesize.sol#5-14) uses inline-assembly
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
    

<br />

## Description:


Typically, the Solidity compiler performs checks to ensure that memory is well-defined and safe. However, when using `inline-assembly`, you can bypass the compiler's checks, potentially leading to memory manipulation.


<br />

## Recommendation:

Be cautious when using `inline assembly.`

<br />

## Exploit scenario:


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


<br />

## Reference:


- https://medium.com/@ac1d_eth/technical-exploration-of-inline-assembly-in-solidity-b7d2b0b2bda8
- [https://solidity-kr.readthedocs.io/ko/latest/assembly.html#:~:text=Inline assembly is a way to access the Ethereum Virtual Machine at a low level. This bypasses several important safety features and checks of Solidity. You should only use it for tasks that need it%2C and only if you are confident with using it](https://solidity-kr.readthedocs.io/ko/latest/assembly.html#:~:text=Inline%20assembly%20is%20a%20way%20to%20access%20the%20Ethereum%20Virtual%20Machine%20at%20a%20low%20level.%20This%20bypasses%20several%20important%20safety%20features%20and%20checks%20of%20Solidity.%20You%20should%20only%20use%20it%20for%20tasks%20that%20need%20it%2C%20and%20only%20if%20you%20are%20confident%20with%20using%20it).    
    

</details>

