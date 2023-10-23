from pathlib import Path
from typing import Dict, List, Set, Tuple, Union, Optional
from collections import defaultdict
from semantic_version import Version
from exceptions import *
import sys
import json
import subprocess

from parse_version_and_install_solc import SolcParser
from compilation_unit import SafeDevCompilationUnit

# from crytic_compile.crytic_compile import CryticCompile
import os

class Filename: #원래 used, short가 있었는데 왜 필요한지 모르겠어서 절대/상대 경로만 우선 넣어둠
    def __init__(self, absolute: str, relative: str):
        self.absolute = absolute
        self.relative = relative
    
    def __hash__(self) -> int:
        return hash(self.relative)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Filename):
            return NotImplemented
        return self.relative == other.relative

    def __repr__(self) -> str:
        return f"Filename(absolute={self.absolute}, relative={self.relative}))"

def convert_filename(filename: str, working_dir: Path):
    if isinstance(filename, Filename):
        return filename

    filename = Path(filename)
    absolute = Path(os.path.abspath(filename))
    try:
        relative = Path(os.path.relpath(filename, Path.cwd()))
    except ValueError:
        relative = Path(filename)


    return Filename(absolute=str(absolute), relative=relative.as_posix())

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
    def dependencies(self) -> Set[str]:
        return self._dependencies
    
    @property
    def working_dir(self) -> Path:
        return self._working_dir
    
    @working_dir.setter
    def working_dir(self, working_dir: Path):
        self._working_dir = working_dir
    
    
    def _get_cached_offset_to_line(self, file: Filename) -> None: #모르겠음
        """Compute the cached offsets to lines

        Args:
            file (Filename): filename
        """
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


    def execute_solc(self, solc_command: str) -> None:
        solc_binary_path = self.solc_binary_path.joinpath(f"solc-{self.solc_version}")

        command: List = [str(solc_binary_path)]

        if isinstance(self.source, (str, Path)):
            command.append(self.source)
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