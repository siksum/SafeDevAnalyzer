from pathlib import Path
from typing import Dict, List

class SafeDevCompile:
    def __init__(self, target):
        self.source = target
        self._working_dir = Path.cwd()
        self._compilation_units: Dict[str, CompilationUnit] = {}

    @property
    def target(self) -> str:
        return self.source
    
    @property
    def compilation_units(self) -> Dict[str, CompilationUnit]:
        return self._compilation_units

    def chekc_multiple_compilation_units(self, contract: str) -> bool:
        count = 0
        for compilation_unit in self._compilation_units.values():
            for source_unit in compilation_unit.source_units.values():
                if contract in source_unit.contracts_names:
                    count += 1
        return count >= 2

    @property
    def filenames(self) -> List[filenames] = None:
        return self._filenames  
    
    def compile(solidity_file, solc_binary_path, solc_version):
        solidity_file, solc_version, solc_binary_path = parser_main(sys.argv[1])
        execute_solc(solidity_file, solc_binary_path, solc_version)