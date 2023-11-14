# Audit Report

> 🔍 `Filename`: test/detector/shift.sol
---

<details>
<summary style='font-size: 20px;'>incorrect-shift</summary>
<div markdown='1'>

## Detect Results

| Detector | Impact | Confidence | Description |
| --- | --- | --- | --- |
| incorrect-shift | High | High | f 함수는 잘못된 shift 연산을 포함하고 있습니다. EXPRESSION a = 8 >>' a |


## Vulnerabiltiy in code:

```solidity
line 13:     function f() internal pure returns (uint a) {

```
 ---

 ```solidity
line 15:             a := sar(a, 8)

```
 ---

 
어셈블리 함수에서 shift 연산을 사용할 때, 파라미터의 순서가 잘못된 경우를 검사합니다.
    

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
`shr(a, 8)`: 변수 a의 비트를 오른쪽으로 8개만큼 시프트합니다. 즉, a의 값을 8비트 오른쪽으로 이동시킵니다.
`shr(8, a)`: 숫자 8을 변수 a의 비트 수만큼 오른쪽으로 시프트합니다. 따라서 a 변수가 어떤 값이든 안전하게 8 비트만큼 오른쪽으로 시프트됩니다.
    
`shl(a, 8)`: a 변수가 시프트됩니다. a 변수의 값과 비트 길이에 따라 결과가 달라질 수 있습니다. 만약 a가 충분히 큰 값을 갖고 있어서 왼쪽 시프트로 인해 비트 길이가 넘어가는 경우, 예상치 못한 값이 발생할 수 있습니다.
`shl(8, a)`: 8이 고정된 값을 시프트하는 것이므로 시프트 연산의 결과는 a 변수의 값에만 의존합니다. 따라서 a 변수가 어떤 값이든 안전하게 8 비트만큼 왼쪽으로 시프트됩니다.

`sar(a, 8)`: 변수 a의 비트를 오른쪽으로 이동시키므로 a의 현재 값에 따라 결과가 달라집니다. 
`sar(8, a)`: 항상 상수 8의 비트 이동 연산을 수행하므로 a의 현재 값에 영향을 받지 않습니다. 따라서 예측 가능하고 일관된 결과를 얻을 수 있습니다.


## Recommendation:


보통은 `sar(8, a)`, `shl(8, a)`, `shr(8, a)`가 더 예측 가능하고 안전한 방법일 수 있습니다. 하지만 실제 상황과 사용하는 데이터에 따라서 다른 방식이 더 적합할 수 있습니다. 이러한 결정은 프로그램의 요구 사항과 목적에 따라 다르므로 주의 깊게 검토하고 적절한 방법을 선택해야 합니다.
또한, solidity yul code는 Overflow/Underflow를 검사하지 않으므로, 이러한 케이스를 고려하여 코드를 작성해야 합니다.
    

</details>

<details>
<summary style='font-size: 20px;'>assembly</summary>
<div markdown='1'>

## Detect Results

| Detector | Impact | Confidence | Description |
| --- | --- | --- | --- |
| assembly | Informational | High | f, 어셈블리 사용
f, 어셈블리 사용
 |


## Vulnerabiltiy in code:

```solidity
line 13:     function f() internal pure returns (uint a) {

```
 ---

 ```solidity
line 14:         assembly {

```
 ---

 

## Exploit scenario:



## Recommendation:



</details>

