from antibug.antibug_compile.compile import SafeDevAnalyzer
from Crytic_compile.utils.naming import Filename, convert_filename
from Crytic_compile import CryticCompile, InvalidCompilation
from pathlib import Path
from  typing import Callable

import sys
import os

def convert_to_json():
    pass

# def convert_relative_path(analyzer: SafeDevAnalyzer):
#     current_working_directory = os.getcwd()
#     while not os.path.basename(current_working_directory) == "SafeDevAnalyzer":
#         current_working_directory = os.path.dirname(current_working_directory)

#     relative_path = os.path.relpath(analyzer.target_path, current_working_directory)
    
#     return Path(relative_path)

def relative_to_short(relative: Path) -> Path:
    return relative

def output_to_info(analyzer: SafeDevAnalyzer): 

    file_path = analyzer.target_list
    
    i = 0
    abi_list = []
    bytecode_list = []

    for crytic_compile in analyzer.crytic_compile:
        filename_object = convert_filename(file_path[i], relative_to_short, crytic_compile)
        print(filename_object)
        abi_list.append(crytic_compile._compilation_units[file_path[i]]._source_units[filename_object].abis)
        bytecode_list.append(crytic_compile._compilation_units[file_path[i]]._source_units[filename_object]._runtime_bytecodes)
        i += 1
    print(abi_list)
    print(bytecode_list)

if __name__ == "__main__":
    analyzer = SafeDevAnalyzer(sys.argv[1])


    output_to_info(analyzer)

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