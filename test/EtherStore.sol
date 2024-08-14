// SPDX-License-Identifier: MIT
pragma solidity ^0.7.1;

contract EtherStore {
    mapping(address => uint) public balances;
    mapping(address => uint) public highScores;
    address public owner;

    modifier onlyOwner {
        require(tx.origin == owner, "Not owner");
        _;
    }

    function deposit() public payable {
        balances[msg.sender] += msg.value;
    }

    function withdraw(uint bal) public{

        (bool sent, ) = msg.sender.call{value: bal}("");
        require(sent, "Failed to send Ether");
    }    

    function guess(uint _guess) public {
        uint answer = uint(
            keccak256(abi.encodePacked(blockhash(block.number - 1), block.timestamp))
        );

        if (_guess == answer) {
            reward(msg.sender);
        }
    }

    function reward(address to) public onlyOwner(){
        (bool sent, ) = to.call{value: 1 ether}("");
        require(sent, "Failed to send Ether");

    }

    function getBalance() public view returns (uint) {
        return address(this).balance;
    }
}