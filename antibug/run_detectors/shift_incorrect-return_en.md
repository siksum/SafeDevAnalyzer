<details>
<summary style='font-size: 20px;'>incorrect-return</summary>
<div markdown='1'>

### Detect Results

| Detector | Impact | Confidence | Info |
|:---:|:---:|:---:|:---:|
| incorrect-return | <span style='color:lightcoral'> High </span> | <span style='color:olivedrab'> Medium </span> | Foo.foo() (test/detector/shift.sol#22-26) calls Bar.blockingFunction() (test/detector/shift.sol#7-11) which halt the execution return(uint256,uint256)(0,0x20) (test/detector/shift.sol#9)
 |||


### Vulnerabiltiy in code:

```solidity
line 22:     function foo() public pure returns(bool) {

```
 ---

 ```solidity
line 7:     function blockingFunction() public pure returns (bool) {

```
 ---

 ```solidity
line 9:             return(0,0x20)

```
 ---

 Detect if `return` in an assembly block halts unexpectedly the execution.

### Exploit scenario:


```solidity
contract C {
    function f() internal returns (uint a, uint b) {
        assembly {
            return (5, 6)
        }
    }

    function g() returns (bool){
        f();
        return true;
    }
}
```
The return statement in `f` will cause execution in `g` to halt.
The function will return 6 bytes starting from offset 5, instead of returning a boolean.

### Recommendation:

Use the `leave` statement.

### Reference:

https://blog.ethereum.org/2019/12/03/ef-supported-teams-research-and-development-update-2019-pt-2#solidity-060:~:text=Add%20%22leave%22%20statement%20to%20Yul%20/%20Inline%20Assembly%20to%20return%20from%20current%20function

</details>

