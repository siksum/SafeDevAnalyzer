import os
import sys
from pathlib import Path
from typing import Dict
from Crytic_compile.naming import convert_filename

from slither_core.slither import Slither
from Crytic_compile import CryticCompile, InvalidCompilation
from antibug.antibug_compile.parse_version_and_install_solc import SolcParser

from Crytic_compile.naming import Filename
class SafeDevAnalyzer():
    def __init__(self, target: str, **kwargs) -> None:
        self.target_path = os.path.abspath(target)
        self.target_name = []
        self.crytic_compile = []
        self.compilation_units: Dict[str, Slither] = {}
        self.target_list = []
        self.abi_list = []
        self.bytecode_list = []

        try:
            if os.path.isdir(self.target_path):
                self.target_list = self.find_all_solidity_files('.sol')
                self.crytic_compile.extend(self.get_crytic_compile_list())
                for crytic, filename in zip(self.crytic_compile, self.target_name):
                    self.compilation_units[filename] = Slither(crytic)
            elif os.path.isfile(self.target_path):
                if self.target_path.endswith('.sol'):
                    self.target_list.append(self.target_path)
                    self.solc_parse = SolcParser(self.target_list[0])
                    self.crytic_compile.append(CryticCompile(self.target_list[0]))
                    self.compilation_units[os.path.basename(
                        self.target_path)] = Slither(self.crytic_compile[0])  
                    # for crytic in self.crytic_compile:
                    #     print("crytic",crytic.compilation_units[self.target_path]._filename_to_contracts)
        except InvalidCompilation:
            print('Not supported file type')
            sys.exit(0)

    def to_deploy(self): 
        file_path = self.target_list
        i = 0
        for crytic_compile in self.crytic_compile:
            filename_object = convert_filename(file_path[i], relative_to_short, crytic_compile)
            self.abi_list.append(crytic_compile._compilation_units[file_path[i]]._source_units[filename_object].abis)
            self.bytecode_list.append(crytic_compile._compilation_units[file_path[i]]._source_units[filename_object]._runtime_bytecodes)
            i += 1
        
        return self.abi_list, self.bytecode_list
    
    def find_all_solidity_files(self, extension: str):
        target_list = []
        for root, dirs, files in os.walk(self.target_path):
            for file in files:
                if file.endswith(extension):
                    file_path = os.path.join(root, file)
                    target_list.append(file_path)
        return target_list
    
    def get_crytic_compile_list(self):
        compilation_units = []
        version = '0.8.0'  # default
        for file in self.target_list:
            try:
                self.target_name.append(os.path.basename(file))
                if (len(version) > 0):
                    self.solc_parse = SolcParser(file)
                compilation_units.append(CryticCompile(file))
            except:
                print('compile error')
        return compilation_units
    
    
def relative_to_short(relative: Path) -> Path:
    return relative




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

# ###### test directory #######  -> done
# instance1 = SafeDevAnalyzer('/Users/sikk/Desktop/AntiBug/development/SafeDevAnalyzer/antibug/compile/test/overflow.sol')
# print(instance1.compilation_units)

# ###### test zip ######### -> not working
# instance2 = SafeDevAnalyzer('/Users/sikk/Desktop/AntiBug/development/SafeDevAnalyzer/antibug/compile/test.zip')
# print(instance2.compilation_units)

# ###### test import #########
# instance3 = SafeDevAnalyzer('/Users/sikk/Desktop/AntiBug/development/SafeDevAnalyzer/antibug/compile/test/import/var.sol')
# print(instance3.compilation_units)

# instance4 = SafeDevAnalyzer('/Users/sikk/Desktop/AntiBug/development/SafeDevAnalyzer/antibug/compile/test/import')
# print(instance4.compilation_units)