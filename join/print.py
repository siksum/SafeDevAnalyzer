result = "# Detect Report\n\n"
result += "## Reentrancy\n\n"
result += """ ```solidity
// SPDX-License-Identifier: MIT
pragma solidity  ^0.8.1;

contract EtherStore {
    mapping(address => uint) public balances;

    function deposit() public payable {
        balances[msg.sender] += msg.value;
    }

    function DreamPlusAcademy() public {
        uint bal = balances[msg.sender];
        require(bal > 0);

        (bool sent, ) = msg.sender.call{value: bal}("");
        require(sent, "Failed to send Ether");

        balances[msg.sender] = 0;
        revert("revert");
    }

    // Helper function to check the balance of this contract
    function getBalance() public view returns (uint) {
        return address(this).balance;
    }
}
``` """
open("../output.md", "w").write(result)
