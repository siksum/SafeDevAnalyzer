<button class='date-button'>2023-11-25</button>

# Audit Report

> 🔍 `Filename`: /Users/sikk/Desktop/Antibug/SafeDevAnalyzer/test/tx.origin.sol
---

[<button class='styled-button'>Korean</button>](tx.origin_kr.md)
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
<summary style='font-size: 20px;'>tx-origin</summary>
<div markdown='1'>

## Detect Results

| Detector | Impact | Confidence | Info |
|:---:|:---:|:---:|:---:|
| tx-origin | <span style='color:olivedrab'> Medium </span> | <span style='color:olivedrab'> Medium </span> | `transfer` uses `tx.origin` for authorization: require(bool,string)(tx.origin == owner,Not owner) (test/tx.origin.sol#31)
 |||


<br />

## Vulnerabiltiy in code:

```solidity
line 31:         require(tx.origin == owner, "Not owner");

```
 ---

 <br />

## Background:


<details> 
    <summary style='font-size: 18px;color:pink;'> 💡 tx.origin and  msg.sender </summary><br />
    
`tx.origin` and `msg.sender` are global variables in Solidity, both representing the address of the caller.

`tx.origin` indicates the address of the account that originally created and transmitted the transaction to the network. <br>
Thus, `tx.origin` always represents the address of an `Externally Owned Account (EOA)`.<br>
It is useful when writing smart contracts that need to identify the original initiator of a transaction, such as in the implementation of multi-signature wallets.

`msg.sender` represents the address of the account that called the currently executing function. <br>
Therefore, `msg.sender` can be either the address of an `EOA` or a `Contract`. <br>
It is useful when writing smart contracts that need to verify the current sender of the message, such as in the implementation of access control features.

<br>

<div class='mermaid'>
flowchart LR
     id1(EOA) --> id2(Contract A) --> id3(Contract B) --> id4(Contract C)
</div>

<br>

If `EOA` calls `Contract A`, `Contract A` calls `Contract B`, and `Contract B` in turn calls `Contract C`, then within `Contract C`, `msg.sender` will be `Contract B`, and `tx.origin` will be `EOA`. <br>
While `msg.sender` and `tx.origin` might appear to represent the same account, `tx.origin` does not represent the address of the caller, but rather the address of the account that originally initiated the contract call.

</details>
<br />
    
    

<br />

## Description:


`tx.origin` can only track the information of the account that originally initiated the transaction.<br>
In complex transactions involving multiple contract calls, there are scenarios where it's necessary to identify the address of the `EOA`.<br>
In such cases, `tx.origin` cannot be used to identify the address of the `EOA`, preventing the implementation of granular access control based on immediate contract interactions.<br>

Additionally, using `tx.origin` for authentication is vulnerable to phishing attacks.    

<p align="center">
<img src="https://i.imgur.com/FGDediO.png" width="700" height="500">
</p>

Attackers can create malicious contracts and entice users to call these contracts. <br>
When a user interacts with a malicious contract, the attacker can capture the user's `EOA (Externally Owned Account)` address. <br>
Subsequently, if the attacker uses the user's `EOA` address to call a contract, `tx.origin` will still point to the user's address, thus mistakenly recognizing the attacker as a legitimate user.<br>
    

<br />

## Recommendation:


Using `tx.origin` limits interoperability between contracts because a contract that uses `tx.origin` cannot be safely used by another contract. <br>
Additionally, according to an answer by `Vitalik Buterin` on [ethereum stackexchange](https://ethereum.stackexchange.com/questions/196/how-do-i-make-my-dapp-serenity-proof/200#200) in July 2016, there is a possibility that `tx.origin` may be removed in future Ethereum protocol updates.<br>

It is safer to perform authentication using `msg.sender` instead of `tx.origin`, as follows.

```solidity
function transfer(address payable _to, uint256 _amount) public {
  require(msg.sender == owner);

  (bool sent, ) = _to.call.value(_amount)("");
  require(sent, "Failed to send Ether");
}
``` 
    

<br />

## Exploit scenario:


```solidity
contract Wallet {
    address public owner;

    constructor() payable {
        owner = msg.sender;
    }

    function transfer(address payable _to, uint _amount) public {
        require(tx.origin == owner, "Not owner");

        (bool sent, ) = _to.call{value: _amount}("");
        require(sent, "Failed to send Ether");
    }
}
```    

Assuming that `Alice` deploys a `Wallet` contract, and a malicious user, `Bob`, deceives `Alice` into calling his `Attack` contract.

<br>

```solidity
contract Attack {
    address payable public owner;
    Wallet wallet;

    constructor(Wallet _wallet) {
        wallet = Wallet(_wallet);
        owner = payable(msg.sender);
    }

    function attack() public {
        wallet.transfer(owner, address(wallet).balance);
    }
}
```

When `Alice` calls the `attack` function of the `Attack` contract, this `Attack` contract then calls the `transfer` function of the `Wallet` contract. <br>
The `transfer` function in the `Wallet` contract performs authentication using `tx.origin`, which points to `Alice`'s address. <br>
Therefore, the `Attack` contract is recognized as an `EOA` with `Alice`'s address, allowing Bob to withdraw Ether from Alice's `Wallet` contract.<br>
 
    

<br />

## Real World Examples:

ddd

<br />

## Reference:


- https://ethereum.stackexchange.com/questions/1891/whats-the-difference-between-msg-sender-and-tx-origin
- https://docs.soliditylang.org/en/v0.8.17/security-considerations.html#tx-origin
- https://stackoverflow.com/questions/73554510/msg-sender-preferred-over-tx-origin-in-solidity
- https://consensys.github.io/smart-contract-best-practices/development-recommendations/solidity-specific/tx-origin/
- https://dev.to/zenodavids/avoiding-security-vulnerabilities-the-txorigin-vs-msgsender-debate-24an    
    

</details>

