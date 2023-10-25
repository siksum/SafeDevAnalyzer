from pathlib import Path
from typing import Dict, List, Set, Tuple, Union, Optional
from collections import defaultdict
from compile.compile_exception import InvalidCompilation
import json
import subprocess

from compile.parse_version_and_install_solc import SolcParser
from compile.compilation_unit import SafeDevCompilationUnit
from compile.filename import Filename, convert_filename

# from Crytic_compile.crytic_compile import CryticCompile
import os


class SafeDevCompile(SolcParser):
    def __init__(self, target: str):
        super().__init__(target)
        
        self._working_dir = Path.cwd()
        self._dependencies: Set = set()
        self._filename: Filename =convert_filename(self.source, self.working_dir)
        
        #self._compilation_units: Dict[str, CompilationUnit] = {}
        self._cached_line_to_code: Dict[Filename, List[bytes]] = {}
        self._cached_line_to_offset: Dict[Filename, Dict[int, int]] = defaultdict(dict)
        self._cached_offset_to_line: Dict[Filename, Dict[int, Tuple[int, int]]] = {}
        self._src_content: Dict = {}
        self._bytecode_only = False
        self._compilation_units: Dict[str, SafeDevCompilationUnit] = {}

    @property
    def target(self) -> str:
        return self.source
    
    @property
    def compilation_units(self) -> Dict[str, SafeDevCompilationUnit]:
        return self._compilation_units
    
    @property
    def filenames(self) -> Set[Filename]: #todo
        filenames: Set[Filename] = set()
        for compile_unit in self._compilation_units.values():
            filenames |= set(compile_unit.filenames)
        return filenames

    @property
    def dependencies(self) -> Set[str]:
        return self._dependencies
    
    @property
    def working_dir(self) -> Path:
        return self._working_dir
    
    @working_dir.setter
    def working_dir(self, working_dir: Path):
        self._working_dir = working_dir
    
    
    def _get_cached_offset_to_line(self, file: Filename) -> None: #모르겠음
        if file not in self._cached_line_to_code:
            self._get_cached_line_to_code(file)

        source_code = self._cached_line_to_code[file]
        acc = 0
        lines_delimiters: Dict[int, Tuple[int, int]] = {}
        for line_number, x in enumerate(source_code):
            self._cached_line_to_offset[file][line_number + 1] = acc

            for i in range(acc, acc + len(x)):
                lines_delimiters[i] = (line_number + 1, i - acc + 1)

            acc += len(x)
        lines_delimiters[acc] = (len(source_code) + 1, 0)
        self._cached_offset_to_line[file] = lines_delimiters

    def _get_cached_line_to_code(self, file: Filename) -> None:
        source_code = self.solidity_file
        source_code_encoded = source_code.encode("utf-8")
        source_code_list = source_code_encoded.splitlines(True)
        self._cached_line_to_code[file] = source_code_list

    def get_line_from_offset(self, filename: Union[Filename, str], offset: int) -> Tuple[int, int]:

        if filename not in self._cached_offset_to_line:
            self._get_cached_offset_to_line(filename)

        lines_delimiters = self._cached_offset_to_line[filename]
        return lines_delimiters[offset]

    def get_global_offset_from_line(self, filename: Union[Filename, str], line: int) -> int:
        if filename not in self._cached_line_to_offset:
            self._get_cached_offset_to_line(filename)

        return self._cached_line_to_offset[filename][line]
    
    def get_code_from_line(self, filename: Union[Filename, str], line: int) -> Optional[bytes]:
        if filename not in self._cached_line_to_code:
            self._get_cached_line_to_code(filename)

        lines = self._cached_line_to_code[filename]
        if line - 1 < 0 or line - 1 >= len(lines):
            return None
        return lines[line - 1]
    
    @property
    def src_content(self) -> Dict[str, str]:
        self._src_content[self._filename.absolute] = self.solidity_file
        return self._src_content

    @src_content.setter
    def src_content(self, src: Dict) -> None:
        self._src_content = src
    
    def src_content_for_file(self, filename_absolute: str) -> Optional[str]:
        return self.src_content.get(filename_absolute, None)
    
    #########################################
    ########## Related Compile #########
    #########################################
  
    @property
    def bytecode_only(self) -> bool:
        return self._bytecode_only

    @bytecode_only.setter
    def bytecode_only(self, bytecode_only: bool) -> None:
        self._bytecode_only = bytecode_only


def execute_solc() -> None:
    solc_binary_path = solc_binary_path.joinpath(f"solc-{solc_version}")

    command: List = [str(solc_binary_path)]

    if isinstance(source, (str, Path)):
        command.append(source)
    option = ["--combined-json", "abi,ast,bin,bin-runtime,srcmap,srcmap-runtime,userdoc,devdoc,hashes", "--allow-paths", "."]
    command.extend(option)
    
    proc = subprocess.Popen(
        command,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        encoding="utf8",
    )

    stdout, stderr = proc.communicate()

    if stderr:
        print("solc stderr:\n%s", stderr) 

    try:
        ret: Dict = json.loads(stdout)
        return ret
    except json.decoder.JSONDecodeError:
        raise InvalidCompilation(f"Invalid solc compilation {stderr}")


# instance = CryticCompile(sys.argv[1])
# print(instance.package_name)
# print("=====================================")

# instance1 = SafeDevCompile(sys.argv[1])
# print(instance1.execute_solc())



# instance2 = SolcParser(sys.argv[1])
# print(instance2.solidity_file)