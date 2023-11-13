// SPDX-License-Identifier: MIT


pragma solidity ^0.8.14;

contract Box {
    uint256 public value;

    function retrieve() public view returns(uint256) {
        assembly {
            let v := sload(0) 
            mstore(0x80, v)
            return(0x80, 32) 
        }
    }

    function store(uint256 newValue) public {
        assembly {
            sstore(0, newValue)
            mstore(0x80, newValue)
            log1(0x80, 0x20, 0xac3e966f295f2d5312f973dc6d42f30a6dc1c1f76ab8ee91cc8ca5dad1fa60fd)
        }
    }
}