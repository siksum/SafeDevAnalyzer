from antibug.compile.safe_dev_analyzer import SafeDevAnalyzer
from slither_core.slithir.operations import BinaryType, Binary
from slither_core.slithir.operations import SolidityCall

instance= SafeDevAnalyzer('roulette.sol')

for compilation in instance.compilation_units.values():
    for contract in compilation.contracts:
        for function in contract.functions:
            for node in function.nodes:
                for ir in node.irs:
                    if isinstance(ir, Binary):
                        print(ir)
                    

### ir               
# TMP_0(uint256) = block.number - 1
# TMP_1(uint256) = SOLIDITY_CALL blockhash(uint256)(TMP_0)
# TMP_2(bytes) = SOLIDITY_CALL abi.encodePacked()(TMP_1,block.timestamp)
# TMP_3(bytes32) = SOLIDITY_CALL keccak256(bytes)(TMP_2)
# TMP_4 = CONVERT TMP_3 to uint256
# answer(uint256) := TMP_4(uint256)
# TMP_5(bool) = _guess == answer
# CONDITION TMP_5
# TUPLE_0(bool,bytes) = LOW_LEVEL_CALL, dest:msg.sender, function:call, arguments:[''] value:1000000000000000000 
# sent(bool)= UNPACK TUPLE_0 index: 0 
# TMP_6(None) = SOLIDITY_CALL require(bool,string)(sent,Failed to send Ether)
