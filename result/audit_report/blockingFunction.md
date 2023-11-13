# Audit Report 

> 🔍 `Filename`: test/detector/incorrect-return/blockingFunction.sol
---

<br></br>
## Detect Results

| Detector | Impact | Confidence | Description | 
| --- | --- | --- | --- | 
| incorrect-return | High | Medium | Foo.foo() (test/detector/incorrect-return/blockingFunction.sol#14-18) calls Bar.blockingFunction() (test/detector/incorrect-return/blockingFunction.sol#5-9) which halt the execution return(uint256,uint256)(0,0x20) (test/detector/incorrect-return/blockingFunction.sol#7)
 | 


<br></br>
## Vulnerabiltiy in code: 

```solidity
line 14:     function foo() public pure returns(bool) {

```
 ---

 ```solidity
line 5:     function blockingFunction() public pure returns (bool) {

```
 ---

 ```solidity
line 7:             return(0,0x20)

```
 ---

 Detect if `return` in an assembly block halts unexpectedly the execution.

<br></br>
## Exploit scenario: 


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

<br></br>
## Recommendation: 

Use the `leave` statement.

## Reference: 

https://blog.ethereum.org/2019/12/03/ef-supported-teams-research-and-development-update-2019-pt-2#solidity-060:~:text=Add%20%22leave%22%20statement%20to%20Yul%20/%20Inline%20Assembly%20to%20return%20from%20current%20function

