// SPDX-License-Identifier: GPL-3.0
pragma solidity ^0.8.4;

error Unauthorized(string message);

contract ErrorContract {
    uint[] dataArray;
    mapping(address => uint) public balances;
    address payable owner = payable(tx.origin);
    uint8 y;
    uint16 z;
    uint32 x = y + z;

    function withdraw() view public {
        try {
            deposit();
            revert("Only owner can withdraw money");
        }
        catch Unauthorized(string memory reason){
        }
    }   
    function deposit() public payable {
        balances[msg.sender] += msg.value;
    }
}

contract EtherStore{
    mapping(address => uint) public balances;
    function deposit() public payable {
        balances[msg.sender] += msg.value;
    }
    function withdraw(uint _amount) public {
        require(balances[msg.sender] >= _amount, "Insufficient balance");
        (bool sent, ) = msg.sender.call{value: _amount}("");
        require(sent, "Failed to send Ether");
        balances[msg.sender] -= _amount;
    }
}