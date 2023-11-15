// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

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