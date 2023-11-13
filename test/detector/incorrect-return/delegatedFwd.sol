// SPDX-License-Identifier: MIT

pragma solidity 0.4.24;


contract ERCProxy {
    uint256 internal constant FORWARDING = 1;
    uint256 internal constant UPGRADEABLE = 2;

    function proxyType() public pure returns (uint256 proxyTypeId);
    function implementation() public view returns (address codeAddr);
}


contract IsContract {
    /*
    * NOTE: this should NEVER be used for authentication
    * (see pitfalls: https://github.com/fergarrui/ethereum-security/tree/master/contracts/extcodesize).
    *
    * This is only intended to be used as a sanity check that an address is actually a contract,
    * RATHER THAN an address not being a contract.
    */
    function isContract(address _target) internal view returns (bool) {
        if (_target == address(0)) {
            return false;
        }

        uint256 size;
        assembly { size := extcodesize(_target) }
        return size > 0;
    }
}

contract DelegateProxy is ERCProxy, IsContract {
    uint256 internal constant FWD_GAS_LIMIT = 10000;

    /**
    * @dev Performs a delegatecall and returns whatever the delegatecall returned (entire context execution will return!)
    * @param _dst Destination address to perform the delegatecall
    * @param _calldata Calldata for the delegatecall
    */
    function delegatedFwd(address _dst, bytes _calldata) internal {
        require(isContract(_dst));
        uint256 fwdGasLimit = FWD_GAS_LIMIT;

        assembly {
            let result := delegatecall(sub(gas, fwdGasLimit), _dst, add(_calldata, 0x20), mload(_calldata), 0, 0)
            let size := returndatasize
            let ptr := mload(0x40)
            returndatacopy(ptr, 0, size)

            // revert instead of invalid() bc if the underlying call failed with invalid() it already wasted gas.
            // if the call returned error data, forward it
            switch result case 0 { revert(ptr, size) }
            default { return(ptr, size) }
        }
    }
}