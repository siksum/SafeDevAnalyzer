import os
from typing import Dict

from slither_core.slither import Slither
from antibug.compile.antibug_compile import AntibugCompile
from antibug.compile.exceptions import InvalidCompilation
from antibug.compile.parse_version_and_install_solc import SolcParser

class SafeDevAnalyzer():
    def __init__(self, file: str, **kwargs) -> None:
        self.file_path = os.path.abspath(file)
        self.file_basename = os.path.basename(file)
        self.file_name = []
        self.antibug_compile = []
        self.compilation_units: Dict[str, Slither] = {}
        self.file_list = []
        self.abi_list = []
        self.bytecode_list = []
        self.solc_parse = None
        
        try:
            if os.path.isdir(self.file_path):
                self.file_list = self.find_all_solidity_files('.sol')
                self.antibug_compile.extend(self.get_antibug_compile_list())
                for crytic, filename in zip(self.antibug_compile, self.file_name):
                    self.compilation_units[filename] = Slither(crytic)
            elif os.path.isfile(self.file_path):
                if self.file_path.endswith('.sol'):
                    self.file_list.append(self.file_path)
                    if self.solc_parse is None:
                        self.solc_parse = SolcParser(self.file_list[0])
                    self.solc_parse.run_parser()                    
                    self.antibug_compile.append(AntibugCompile(self.file_list[0], self.solc_parse._solc_binary_version))
                    
                    self.compilation_units[os.path.basename(self.file_path)] = Slither(self.antibug_compile[0]) 
                    
        except InvalidCompilation:
            return

    def to_compile(self): 
        file_path = self.file_list
        i = 0
        for antibug_compile in self.antibug_compile:
            filename_object = antibug_compile.filename_lookup(file_path[i])
            self.abi_list.append(antibug_compile._compilation_units[file_path[i]]._source_units[filename_object].abis)
            self.bytecode_list.append(antibug_compile._compilation_units[file_path[i]]._source_units[filename_object]._init_bytecodes)
            i += 1
        return self.abi_list, self.bytecode_list
    
    def find_all_solidity_files(self, extension: str):
        file_list = []
        for root, dirs, files in os.walk(self.file_path):
            for file in files:
                if file.endswith(extension):
                    file_path = os.path.join(root, file)
                    file_list.append(file_path)
        return file_list
    
    def get_antibug_compile_list(self):
        compilation_units = []
        for file in self.file_list:
            try:
                self.file_name.append(os.path.basename(file))
                self.solc_parse = SolcParser(file)
                self.solc_parse.run_parser()
                compilation_units.append(AntibugCompile(file, self.solc_parse._solc_binary_version))
            except:
                print('compile error')
        return compilation_units