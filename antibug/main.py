from antibug.antibug_compile.compile import SafeDevAnalyzer
from Crytic_compile.utils.naming import Filename, convert_filename
from Crytic_compile import CryticCompile, InvalidCompilation
from pathlib import Path
from  typing import Callable

import sys
import os
import json

def convert_to_json(abi_list, bytecode_list):
    combined_data = {}

    for abi, bytecode in zip(abi_list, bytecode_list):
        # abi와 bytecode의 키(예: 'EtherGame')를 가져옴
        key = next(iter(abi))
        
        # 해당 키에 대한 데이터가 이미 combined_data에 있다면, 데이터를 업데이트
        if key in combined_data:
            combined_data[key]['abis'].extend(abi[key])
            combined_data[key]['bytecodes'] = ("0x"+bytecode[key]) # bytecode는 덮어씌우는 형태로 합니다.
        else:
            combined_data[key] = {
                "abis": abi[key],
                "bytecodes": "0x"+bytecode[key]
            }


    combined_json = json.dumps(combined_data, indent=4)
    open ("abi_bytecode.json", "w").write(combined_json)

def relative_to_short(relative: Path) -> Path:
    return relative

def output_for_deploy(analyzer: SafeDevAnalyzer): 
    file_path = analyzer.target_list

    i = 0
    abi_list = []
    bytecode_list = []

    for crytic_compile in analyzer.crytic_compile:
        filename_object = convert_filename(file_path[i], relative_to_short, crytic_compile)
        abi_list.append(crytic_compile._compilation_units[file_path[i]]._source_units[filename_object].abis)
        bytecode_list.append(crytic_compile._compilation_units[file_path[i]]._source_units[filename_object]._runtime_bytecodes)
        i += 1
        
    return abi_list, bytecode_list

if __name__ == "__main__":
    analyzer = SafeDevAnalyzer(sys.argv[1])
    abi_list, bytecode_list = output_for_deploy(analyzer)
    convert_to_json(abi_list, bytecode_list)

# instance = SafeDevAnalyzer('/Users/sikk/Desktop/AntiBug/development/SafeDevAnalyzer/antibug/compile/test/overflow.sol')
# file= '/Users/sikk/Desktop/AntiBug/development/SafeDevAnalyzer/antibug/compile/test/overflow.sol'
# object=Filename(absolute='/Users/sikk/Desktop/AntiBug/development/SafeDevAnalyzer/antibug/compile/test/overflow.sol', used='/Users/sikk/Desktop/AntiBug/development/SafeDevAnalyzer/antibug/compile/test/overflow.sol', relative='test/overflow.sol', short='test/overflow.sol')
# abis =instance.crytic_compile[0]._compilation_units[file]._source_units[object].abis
# runtime_bytecodes = instance.crytic_compile[0]._compilation_units[file]._source_units[object]._runtime_bytecodes

# combined_data = {
#     "abis": abis,
#     "bytecodes": runtime_bytecodes
# }

# combined_json = json.dumps(combined_data, indent=4)
# print("abi and bytecode")
# print(combined_json)
# print()

# print("compilation units")
# print(instance.crytic_compile[0])