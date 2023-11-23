// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;
contract GuessTheRandomNumber {
    constructor() payable {}
    function guess(uint _guess) public {
        uint answer = uint(
            keccak256(abi.encodePacked(blockhash(block.number - 1), block.timestamp))
        );
        // uint answer = uint(
        //     blockhash(block.number - 1)
        // );
 
        if (_guess == answer) {
            (bool sent, ) = msg.sender.call{value: 1 ether}("");
            require(sent, "Failed to send Ether");
        }
    }
 }

//  contract Game {

//     uint reward_determining_number;

//     // function guessing() external{
    //   reward_determining_number = uint256(blockhash(10000)) % 10;
    // }

    // function random() view public returns (uint8) {
    //     return uint8(uint256(keccak256(abi.encodePacked(block.timestamp, block.difficulty)))%256);
    // }

//     function play() public payable {
// 	require(msg.value >= 1 ether);
//     if (uint(blockhash(block.number)) % 2 == 0) {
//         address payable recipient = payable(msg.sender);
//         recipient.transfer(address(this).balance);
//     }

//     }
// }
