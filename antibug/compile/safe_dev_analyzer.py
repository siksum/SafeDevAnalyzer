import os
from typing import Dict

from slither_core.slither import Slither
from antibug.compile.antibug_compile import AntibugCompile
from antibug.compile.exceptions import InvalidCompilation
from antibug.compile.parse_version_and_install_solc import SolcParser

class SafeDevAnalyzer():
    def __init__(self, target: str, **kwargs) -> None:
        self.target_path = os.path.abspath(target)
        self.target_name = []
        self.crytic_compile = []
        self.compilation_units: Dict[str, Slither] = {}
        self.target_list = []
        self.abi_list = []
        self.bytecode_list = []
        self.solc_parse = None
        
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
                    self.solc_parse.run_parser()
                    self.crytic_compile.append(AntibugCompile(self.target_list[0], self.solc_parse._solc_binary_version))
                    self.compilation_units[os.path.basename(
                        self.target_path)] = Slither(self.crytic_compile[0])  
        except InvalidCompilation:
            print('Not supported file type')
            return

    def to_deploy(self): 
        file_path = self.target_list
        i = 0
        for crytic_compile in self.crytic_compile:
            filename_object = crytic_compile.filename_lookup(file_path[i])
            self.abi_list.append(crytic_compile._compilation_units[file_path[i]]._source_units[filename_object].abis)
            self.bytecode_list.append(crytic_compile._compilation_units[file_path[i]]._source_units[filename_object]._init_bytecodes)
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
        for file in self.target_list:
            try:
                self.target_name.append(os.path.basename(file))
                self.solc_parse = SolcParser(file)
                self.solc_parse.run_parser()
                compilation_units.append(AntibugCompile(file, self.solc_parse._solc_binary_version))
            except:
                print('compile error')
        return compilation_units
