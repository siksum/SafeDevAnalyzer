<details>
<summary style='font-size: 20px;'>incorrect-shift</summary>
<div markdown='1'>

### Detect Results

| Detector | Impact | Confidence | Info |
|:---:|:---:|:---:|:---:|
| incorrect-shift | <span style='color:lightcoral'> High </span> | <span style='color:lightcoral'> High </span> | Bar.f() (test/detector/shift.sol#13-17) contains an incorrect shift operation: a = 8 >>' a (test/detector/shift.sol#15)
 |||


### Vulnerabiltiy in code:

```solidity
line 13:     function f() internal pure returns (uint a) {

```
 ---

 ```solidity
line 15:             a := sar(a, 8)

```
 ---

 When using shift operations in an assembly function, it is important to check for cases where the parameters are in the wrong order.

### Exploit scenario:


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


### Recommendation:


In general, `sar(8, a)`, `shl(8, a)` and `shr(8, a)` can be more predictable and safer approaches. However, the choice of method may vary depending on the specific circumstances and the data being used. The decision should be made carefully, taking into account the requirements and goals of the program.
Furthermore, Solidity Yul code does not check for Overflow/Underflow, so you should write your code with these cases in mind and handle them appropriately.


### Reference:


- https://ethereum.stackexchange.com/questions/127538/right-shift-not-working-in-inline-assembly
- https://docs.soliditylang.org/en/v0.8.23/types.html#value-types:~:text=Before%20version%200.5.0%20a%20right%20shift%20x%20%3E%3E%20y%20for%20negative%20x%20was%20equivalent%20to%20the%20mathematical%20expression%20x%20/%202**y%20rounded%20towards%20zero%2C%20i.e.%2C%20right%20shifts%20used%20rounding%20up%20(towards%20zero)%20instead%20of%20rounding%20down%20(towards%20negative%20infinity).
- https://docs.soliditylang.org/en/v0.8.23/types.html#value-types:~:text=Overflow%20checks%20are%20never%20performed%20for%20shift%20operations%20as%20they%20are%20done%20for%20arithmetic%20operations.%20Instead%2C%20the%20result%20is%20always%20truncated.    
    

</details>
