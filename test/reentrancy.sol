// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract EtherStore {
    mapping(address => uint) public balances;

    function deposit() public payable {
        balances[msg.sender] += msg.value;
    }

    function withdraw() public {
        uint bal = balances[msg.sender];
        require(bal > 0);

        (bool sent, ) = msg.sender.call{value: bal}("");
        require(sent, "Failed to send Ether");

        balances[msg.sender] = 0;
    }

    // Helper function to check the balance of this contract
    function getBalance() public view returns (uint) {
        return address(this).balance;
    }
}

// contract TimeLock {
//     mapping(address => uint) public balances;
//     mapping(address => uint) public lockTime;

//     function deposit() external payable {
//         balances[msg.sender] += msg.value;
//         lockTime[msg.sender] = block.timestamp + 1 weeks;
//     }

//     function increaseLockTime(uint _secondsToIncrease) public {
//         lockTime[msg.sender] += _secondsToIncrease;
//     }

//     function withdraw() public {
//         require(balances[msg.sender] > 0, "Insufficient funds");
//         require(
//             block.timestamp > lockTime[msg.sender],
//             "Lock time not expired"
//         );

//         uint amount = balances[msg.sender];
//         balances[msg.sender] = 0;

//         (bool sent, ) = msg.sender.call{value: amount}("");
//         require(sent, "Failed to send Ether");
//     }
// }
