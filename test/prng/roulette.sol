pragma solidity ^0.5.16;

contract Roulette {
    uint public pastBlockTime;

    constructor() public payable {}

    function spin() external payable {
        require(msg.value == 10 ether); // must send 10 ether to play
        require(now != pastBlockTime); // only 1 transaction per block

        pastBlockTime = block.timestamp;

        if(now % 15 == 0) {
            (bool sent, ) = msg.sender.call.value(address(this).balance)("");
            require(sent, "Failed to send Ether");
        }
    }
}