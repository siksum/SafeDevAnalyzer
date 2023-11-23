from antibug.compile.safe_dev_analyzer import SafeDevAnalyzer
from slither_core.slithir.operations import BinaryType, Binary
from slither_core.slithir.operations import SolidityCall
from slither_core.slithir.operations.assignment import Assignment
from slither_core.slithir.operations.type_conversion import TypeConversion
from slither_core.core.declarations.solidity_variables import SOLIDITY_VARIABLES_COMPOSED, SOLIDITY_VARIABLES


from slither_core.core.declarations.solidity_variables import (
    SolidityVariable,
    SolidityFunction,
    SolidityVariableComposed,
)
from slither_core.analyses.data_dependency.data_dependency import is_dependent

instance= SafeDevAnalyzer('roulette.sol')
check_list = ['block.number', 'blockhash', 'block.timestamp', 'now', 'block.gamlimit', 'block.difficulty', 'block.coinbase', 'block.basefee', 'block.prevrandao', 'block.prevhash', 'block.chainid' ]
lvalue = []
convert_value = []
assignment_value = []
results = []
for compilation in instance.compilation_units.values():
    for contract in compilation.contracts:
        for function in contract.functions:
            for node in function.nodes:
                for ir in node.irs:
                    # print(ir)
                    if isinstance(ir, SolidityCall):
                        if ir.function == SolidityFunction('keccak256(bytes)') or ir.function == SolidityFunction('blockhash(uint256)'):
                            if any(word in str(ir.expression) for word in SOLIDITY_VARIABLES_COMPOSED.keys()):
                                lvalue.append(ir.lvalue.name)
                                results.append(ir.expression)
                    if isinstance(ir, TypeConversion):
                        if str(ir.variable) in lvalue:
                            convert_value.append(ir.lvalue.name)
                    if isinstance(ir, Assignment):
                        if str(ir.rvalue.name) in convert_value :
                            assignment_value.append(ir.lvalue.name)
                    if node.contains_if() or node.contains_require_or_assert():
                        for var in node.variables_read:
                            if str(var) in assignment_value:
                                results.append(ir.expression)
for result in results:
    print(result)
        
       
       
# TMP_0(uint256) = block.number - 1
# TMP_1(uint256) = SOLIDITY_CALL blockhash(uint256)(TMP_0)
# TMP_2 = CONVERT TMP_1 to uint256
# answer(uint256) := TMP_2(uint256)
# TMP_3(bool) = _guess == answer
# CONDITION TMP_3
# TUPLE_0(bool,bytes) = LOW_LEVEL_CALL, dest:msg.sender, function:call, arguments:[''] value:1000000000000000000 
# sent(bool)= UNPACK TUPLE_0 index: 0 
# TMP_4(None) = SOLIDITY_CALL require(bool,string)(sent,Failed to send Ether)       
       
                    

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


