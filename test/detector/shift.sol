//SPDX-License-Identifier: GPL-3.0-or-later
pragma solidity ^0.7.0;


contract Bar {

    // function blockingFunction() public pure returns (bool) {
    //     assembly {
    //         return(0,0x20)
    //     }
    // }

    function f() internal pure returns (uint a) {
        assembly {
            a := sar(a, 8)
        }
    }
}

// contract Foo is Bar {

//     function foo() public pure returns(bool) {
//         bool result = blockingFunction();
//         require(result == true, "msg");
//         return result;
//     }
// }