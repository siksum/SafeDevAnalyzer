# Audit Report

> 🔍 `Filename`: test/detector/shift.sol
---

<details>
<summary style='font-size: 20px;'>incorrect-shift</summary>
<div markdown='1'>

## Detect Results

| Detector | Impact | Confidence | Info |
|:---:|:---:|:---:|:---:|
| incorrect-shift | <span style='color:lightcoral'> High </span> | <span style='color:lightcoral'> High </span> | Bar.f() (test/detector/shift.sol#13-17) contains an incorrect shift operation: a = 8 >>' a (test/detector/shift.sol#15)
 |||


## Vulnerabiltiy in code:

```solidity
line 13:     function f() internal pure returns (uint a) {

```
 ---

 ```solidity
line 15:             a := sar(a, 8)

```
 ---

 When using shift operations in an assembly function, it is important to check for cases where the parameters are in the wrong order.

## Exploit scenario:


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

`sar(a, 8)`: This operation shifts the bits of variable `a` to the right, so the result depends on the current value of `a`.
`sar(8, a)`: This operation always performs a bitwise right shift by the constant value 8, regardless of the current value of variable `a`. Therefore, it provides predictable and consistent results.


## Recommendation:


In general, `sar(8, a)`, `shl(8, a)` and `shr(8, a)` can be more predictable and safer approaches. However, the choice of method may vary depending on the specific circumstances and the data being used. The decision should be made carefully, taking into account the requirements and goals of the program.
Furthermore, Solidity Yul code does not check for Overflow/Underflow, so you should write your code with these cases in mind and handle them appropriately.


## Reference:


- https://ethereum.stackexchange.com/questions/127538/right-shift-not-working-in-inline-assembly
- https://docs.soliditylang.org/en/v0.8.23/types.html#value-types:~:text=Before%20version%200.5.0%20a%20right%20shift%20x%20%3E%3E%20y%20for%20negative%20x%20was%20equivalent%20to%20the%20mathematical%20expression%20x%20/%202**y%20rounded%20towards%20zero%2C%20i.e.%2C%20right%20shifts%20used%20rounding%20up%20(towards%20zero)%20instead%20of%20rounding%20down%20(towards%20negative%20infinity).
- https://docs.soliditylang.org/en/v0.8.23/types.html#value-types:~:text=Overflow%20checks%20are%20never%20performed%20for%20shift%20operations%20as%20they%20are%20done%20for%20arithmetic%20operations.%20Instead%2C%20the%20result%20is%20always%20truncated.    
    

</details>

<details>
<summary style='font-size: 20px;'>assembly</summary>
<div markdown='1'>

## Detect Results

| Detector | Impact | Confidence | Info |
|:---:|:---:|:---:|:---:|
| assembly | <span style='color:skyblue'> Informational </span> | <span style='color:sandybrown'> Low </span> | Function Bar.f() (test/detector/shift.sol#13-17) uses inline-assembly
 |||


## Vulnerabiltiy in code:

```solidity
line 13:     function f() internal pure returns (uint a) {

```
 ---

 
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


## Recommendation:

Be cautious when using `inline assembly.`

## Reference:


- https://medium.com/@ac1d_eth/technical-exploration-of-inline-assembly-in-solidity-b7d2b0b2bda8
- [https://solidity-kr.readthedocs.io/ko/latest/assembly.html#:~:text=Inline assembly is a way to access the Ethereum Virtual Machine at a low level. This bypasses several important safety features and checks of Solidity. You should only use it for tasks that need it%2C and only if you are confident with using it](https://solidity-kr.readthedocs.io/ko/latest/assembly.html#:~:text=Inline%20assembly%20is%20a%20way%20to%20access%20the%20Ethereum%20Virtual%20Machine%20at%20a%20low%20level.%20This%20bypasses%20several%20important%20safety%20features%20and%20checks%20of%20Solidity.%20You%20should%20only%20use%20it%20for%20tasks%20that%20need%20it%2C%20and%20only%20if%20you%20are%20confident%20with%20using%20it).    
    

</details>

