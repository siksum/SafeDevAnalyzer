<button class='date-button'>2023-11-20</button>

# Audit Report

> 🔍 `Filename`: /Users/sikk/Desktop/Antibug/SafeDevAnalyzer/test/detector/shift.sol
---

[<button class='styled-button'>English</button>](shift_en.md)
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
<summary style='font-size: 20px;'>incorrect-shift</summary>
<div markdown='1'>

## Detect Results

| Detector | Impact | Confidence | Info |
|:---:|:---:|:---:|:---:|
| incorrect-shift | <span style='color:lightcoral'> High </span> | <span style='color:lightcoral'> High </span> |  `Bar.f()` 함수는 잘못된 shift 연산을 포함하고 있습니다. `a = 8 >>' a` |||


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
    

## Reference:


- https://ethereum.stackexchange.com/questions/127538/right-shift-not-working-in-inline-assembly
- https://docs.soliditylang.org/en/v0.8.23/types.html#value-types:~:text=Before%20version%200.5.0%20a%20right%20shift%20x%20%3E%3E%20y%20for%20negative%20x%20was%20equivalent%20to%20the%20mathematical%20expression%20x%20/%202**y%20rounded%20towards%20zero%2C%20i.e.%2C%20right%20shifts%20used%20rounding%20up%20(towards%20zero)%20instead%20of%20rounding%20down%20(towards%20negative%20infinity).
- https://docs.soliditylang.org/en/v0.8.23/types.html#value-types:~:text=Overflow%20checks%20are%20never%20performed%20for%20shift%20operations%20as%20they%20are%20done%20for%20arithmetic%20operations.%20Instead%2C%20the%20result%20is%20always%20truncated.    
    

</details>

