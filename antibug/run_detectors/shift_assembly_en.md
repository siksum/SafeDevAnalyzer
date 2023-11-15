<details>
<summary style='font-size: 20px;'>assembly</summary>
<div markdown='1'>

### Detect Results

| Detector | Impact | Confidence | Info |
|:---:|:---:|:---:|:---:|
| assembly | <span style='color:skyblue'> Informational </span> | <span style='color:sandybrown'> Low </span> | Function Bar.blockingFunction() (test/detector/shift.sol#7-11) uses inline-assembly
 |||


### Vulnerabiltiy in code:

```solidity
line 7:     function blockingFunction() public pure returns (bool) {

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


### Exploit scenario:


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


### Recommendation:

Be cautious when using `inline assembly.`

### Reference:


- https://medium.com/@ac1d_eth/technical-exploration-of-inline-assembly-in-solidity-b7d2b0b2bda8
- [https://solidity-kr.readthedocs.io/ko/latest/assembly.html#:~:text=Inline assembly is a way to access the Ethereum Virtual Machine at a low level. This bypasses several important safety features and checks of Solidity. You should only use it for tasks that need it%2C and only if you are confident with using it](https://solidity-kr.readthedocs.io/ko/latest/assembly.html#:~:text=Inline%20assembly%20is%20a%20way%20to%20access%20the%20Ethereum%20Virtual%20Machine%20at%20a%20low%20level.%20This%20bypasses%20several%20important%20safety%20features%20and%20checks%20of%20Solidity.%20You%20should%20only%20use%20it%20for%20tasks%20that%20need%20it%2C%20and%20only%20if%20you%20are%20confident%20with%20using%20it).    
    

</details>

