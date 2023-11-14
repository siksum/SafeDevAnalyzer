# Audit Report 

> 🔍 `Filename`: test/detector/incorrect-return/blockingFunction.sol
---

<details>
<summary style='font-size: 20px;'>incorrect-return</summary>
<div markdown='1'>

## Detect Results

| Detector | Impact | Confidence | Description | 
| --- | --- | --- | --- | 
| incorrect-return | High | Medium | 함수 foo가 함수 blockingFunction를 호출하면, EXPRESSION return(uint256,uint256)(0,0x20)으로 인해 실행 흐름이 중단됩니다.
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

 inline assembly block에 return이 사용되면 예기치 않은 실행 흐름이 중단될 수 있습니다.

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
f 함수의 return 문은 g 함수의 실행을 중단시킵니다.
g 함수를 호출하여 true 값을 반환할 것을 기대했으나 f 함수에서 5번째 offset부터 6바이트를 반환한 뒤 실행이 중단됩니다.

<br></br>
## Recommendation: 

0.6.0 이상 버전부터 leave 키워드가 등장하였습니다. 만약 이전 버전을 사용한다면, 0.6.0 이상 버전으로 변경한 후, solidity의 leave 문을 사용하세요.

## Reference: 

https://blog.ethereum.org/2019/12/03/ef-supported-teams-research-and-development-update-2019-pt-2#solidity-060:~:text=Add%20%22leave%22%20statement%20to%20Yul%20/%20Inline%20Assembly%20to%20return%20from%20current%20function

