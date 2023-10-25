import os
import sys
from pathlib import Path
from typing import Dict, Optional
from zipfile import ZipFile
import json

from slither_core.slither import Slither
from Crytic_compile import CryticCompile, InvalidCompilation, is_supported
from solc_select.solc_select import switch_global_version
import antibug.compile.solc_parse.parser_function as ps
from antibug.antibug_compile.parse_version_and_install_solc import SolcParser

from Crytic_compile.utils.naming import Filename
class SafeDevAnalyzer():
    def __init__(self, target: str, **kwargs) -> None:
        self.target_path = os.path.abspath(target)
        self.target_name = []
        self.crytic_compile = []
        self.compilation_units: Dict[str, Slither] = {}

        try:
            if os.path.isdir(self.target_path):
                print('is dir') 
                self.target_list = self.find_all_solidity_files('.sol')
                self.crytic_compile.extend(self.get_crytic_compile_list())
                for crytic, filename in zip(self.crytic_compile, self.target_name):
                    self.compilation_units[filename] = Slither(crytic)

            elif os.path.isfile(self.target_path):
                if self.target_path.endswith('.sol'):
                    print('is sol')
                    self.solc_parse = SolcParser(self.target_path)
                    self.crytic_compile.append(CryticCompile(self.target_path))
                    self.compilation_units[os.path.basename(
                        self.target_path)] = Slither(self.crytic_compile[0])
                elif self.target_path.endswith('.zip') or is_supported(self.target_path):
                    print('is zip')
                    self.crytic_compile.extend(self.load_from_zip())
                    for crytic, filename in zip(self.crytic_compile, self.target_name):
                        self.compilation_units[filename] = Slither(crytic)
                    
        except InvalidCompilation:
            print('Not supported file type')
            sys.exit(0)

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

    def load_from_zip(self):
        compilation_units = []
        target_list = []
        with ZipFile(self.target_path, "r") as file_desc:
            for project in file_desc.namelist():
                if project.endswith('.sol'):
                    target_list.append(os.path.join(
                        os.path.dirname(self.target_path), project))
            for file in target_list:
                self.target_name.append(os.path.basename(file))
                try:
                    self.solc_parse = SolcParser(file)
                    compilation_units.append(CryticCompile(file))
                    print('compile success')
                except:
                    print('not .sol file')
        return compilation_units


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
    
instance = SafeDevAnalyzer('/Users/sikk/Desktop/AntiBug/development/SafeDevAnalyzer/antibug/compile/test')
print(instance.compilation_units)
