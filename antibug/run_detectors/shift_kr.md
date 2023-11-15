# Audit Report

> 🔍 `Filename`: `/Users/sikk/Desktop/Antibug/SafeDevAnalyzer/antibug/run_detectors/shift.sol`
---

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

<details>
<summary style='font-size: 20px;'>incorrect-return</summary>
<div markdown='1'>

## Detect Results

| Detector | Impact | Confidence | Info |
|:---:|:---:|:---:|:---:|
| incorrect-return | <span style='color:lightcoral'> High </span> | <span style='color:olivedrab'> Medium </span> | 함수 `Foo.foo()`가 함수 `Bar.blockingFunction()`를 호출하면, `return(uint256,uint256)(0,0x20)`으로 인해 실행 흐름이 중단됩니다.
 |||


## Vulnerabiltiy in code:

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

## Reference:

https://blog.ethereum.org/2019/12/03/ef-supported-teams-research-and-development-update-2019-pt-2#solidity-060:~:text=Add%20%22leave%22%20statement%20to%20Yul%20/%20Inline%20Assembly%20to%20return%20from%20current%20function

</details>

<details>
<summary style='font-size: 20px;'>assembly</summary>
<div markdown='1'>

## Detect Results

| Detector | Impact | Confidence | Info |
|:---:|:---:|:---:|:---:|
| assembly | <span style='color:skyblue'> Informational </span> | <span style='color:sandybrown'> Low </span> | 함수 `Bar.blockingFunction()`에서 `inline-assembly`가 사용되었습니다.
 |||


## Vulnerabiltiy in code:

```solidity
line 7:     function blockingFunction() public pure returns (bool) {

```
 ---

 
<details> 
    <summary style='font-size: 18px;color:pink;'> 💡 Inline Assembly란? </summary><br />
    
`inline-assembly`는 EVM에 직접적으로 상호작용하며 high-level에서 할 수 없는 수준의 control과 정밀도를 부여합니다.

구체적으로, 가스 사용량을 조정하거나, 특정 EVM 기능에 액세스할 수 있습니다.

solidity에서는 EVM bytecode로 컴파일하도록 설계된 중간 언어인 Yul을 사용하여 `inline-assembly`를 작성할 수 있습니다.

    assembly{ … }
형태로 작성합니다.

</details>
<br />

일반적으로 solidity 컴파일러는 메모리가 잘 정의되어 있는지 확인하고 있지만, `inline-assembly`를 사용하면 컴파일러의 검사를 벗어나기 때문에 메모리 조작으로 이어질 수 있습니다.
    


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
`deposit` 함수에서 `amount`를 `balance`에 더할 때 `add` 명령을 사용하고 있습니다.
`balance`가 최댓값이 255에 가까워진 상태에서 더하려고 하면 오버플로우가 발생하여 `balance`가 감소할 수 있습니다.


## Recommendation:

`inline assembly` 사용에 주의하세요.

## Reference:


- https://medium.com/@ac1d_eth/technical-exploration-of-inline-assembly-in-solidity-b7d2b0b2bda8
- [https://solidity-kr.readthedocs.io/ko/latest/assembly.html#:~:text=Inline assembly is a way to access the Ethereum Virtual Machine at a low level. This bypasses several important safety features and checks of Solidity. You should only use it for tasks that need it%2C and only if you are confident with using it](https://solidity-kr.readthedocs.io/ko/latest/assembly.html#:~:text=Inline%20assembly%20is%20a%20way%20to%20access%20the%20Ethereum%20Virtual%20Machine%20at%20a%20low%20level.%20This%20bypasses%20several%20important%20safety%20features%20and%20checks%20of%20Solidity.%20You%20should%20only%20use%20it%20for%20tasks%20that%20need%20it%2C%20and%20only%20if%20you%20are%20confident%20with%20using%20it).    
    

</details>

