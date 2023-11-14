//SPDX-License-Identifier: GPL-3.0-or-later
pragma solidity ^0.7.0;


contract Shift{
    function shift(int val) public pure returns(int) {
        int res;
        assembly {
            let m := mload(0x40)
            mstore(m, shr(2, val))
            mstore(0x40, add(m, 0x20))
            res := mload(m)
        }

        return res;
    }
    function f() internal returns (uint a) {
        assembly {
            a := shr(a, 8)
        }
    }

}
