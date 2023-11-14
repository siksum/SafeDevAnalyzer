# Audit Report

> 🔍 `Filename`: test/detector/shift.sol
---

<details>
<summary style='font-size: 20px;'>incorrect-shift</summary>
<div markdown='1'>

## Detect Results

| Detector | Impact | Confidence | Description |
| --- | --- | --- | --- |
| incorrect-shift | High | High | f 함수는 잘못된 shift 연산을 포함하고 있습니다. EXPRESSION a = 8 >> a |


## Vulnerabiltiy in code:

```solidity
line 15:             a := shr(a, 8)

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


## Recommendation:


보통은 `shl(8, a)`, `shr(8, a)`가 더 예측 가능하고 안전한 방법일 수 있습니다. 하지만 실제 상황과 사용하는 데이터에 따라서 다른 방식이 더 적합할 수 있습니다. 이러한 결정은 프로그램의 요구 사항과 목적에 따라 다르므로 주의 깊게 검토하고 적절한 방법을 선택해야 합니다.
또한, solidity yul code는 Overflow/Underflow를 검사하지 않으므로, 이러한 케이스를 고려하여 코드를 작성해야 합니다.
    

</details>

<details>
<summary style='font-size: 20px;'>incorrect-return</summary>
<div markdown='1'>

## Detect Results

| Detector | Impact | Confidence | Description |
| --- | --- | --- | --- |
| incorrect-return | High | Medium | 함수 foo가 함수 blockingFunction를 호출하면, EXPRESSION return(uint256,uint256)(0,0x20)으로 인해 실행 흐름이 중단됩니다.
 |


## Vulnerabiltiy in code:

```solidity
line 9:             return(0,0x20)

```
 ---

inline assembly block에 return이 사용되면 예기치 않은 실행 흐름이 중단될 수 있습니다.

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

## Recommendation:

0.6.0 이상 버전부터 leave 키워드가 등장하였습니다. 만약 이전 버전을 사용한다면, 0.6.0 이상 버전으로 변경한 후, solidity의 leave 문을 사용하세요.

</details>

