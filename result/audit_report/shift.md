# Audit Report

> 🔍 `Filename`: ./test/detector/shift.sol
---

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

