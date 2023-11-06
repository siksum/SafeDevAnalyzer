"""
AntibugCompile main module. Handle the compilation.
"""

import logging
import os
import re

from collections import defaultdict
from pathlib import Path
from typing import TYPE_CHECKING, Dict, List, Optional, Set, Tuple, Union

from antibug.compile.compilation_unit import CompilationUnit
from antibug.compile.solc import Solc
from antibug.compile.utils.naming import Filename

# Cycle dependency
if TYPE_CHECKING:
    pass

LOGGER = logging.getLogger("AntibugCompile")
logging.basicConfig()


# pylint: disable=too-many-lines
def _extract_libraries(libraries_str: Optional[str]) -> Optional[Dict[str, int]]:

    if not libraries_str:
        return None
    # Extract tuple like (libname1, 0x00)
    pattern = r"\((?P<name>\w+),\s*(?P<value1>0x[0-9a-fA-F]{2,40})\),?"
    matches = re.findall(pattern, libraries_str)

    if not matches:
        raise ValueError(
            f"Invalid library linking directive\nGot:\n{libraries_str}\nExpected format:\n(libname1, 0x00),(libname2, 0x02)"
        )

    ret: Dict[str, int] = {}
    for key, value in matches:
        ret[key] = int(value, 16) if value.startswith("0x") else int(value)
    return ret


# pylint: disable=too-many-instance-attributes
class AntibugCompile:
    """
    Main class.
    """

    # pylint: disable=too-many-branches
    def __init__(self, target: Union[str, Solc], binary: str, **kwargs: str) -> None:
        """See https://github.com/crytic/crytic-compile/wiki/Configuration
        Target is usually a file or a project directory. It can be an AbstractPlatform
        for custom setup

        Args:
            target (Union[str, AbstractPlatform]): Target
            **kwargs: additional arguments
        """

        # dependencies is needed for platform conversion
        self._dependencies: Set = set()

        self._src_content: Dict = {}

        # Mapping each file to
        #  offset -> line, column
        # This is not memory optimized, but allow an offset lookup in O(1)
        # Because we frequently do this lookup in Slither during the AST parsing
        # We decided to favor the running time versus memory
        self._cached_offset_to_line: Dict[Filename, Dict[int, Tuple[int, int]]] = {}
        # Lines are indexed from 1
        self._cached_line_to_offset: Dict[Filename, Dict[int, int]] = defaultdict(dict)

        # Return the line from the line number
        # Note: line 1 is at index 0
        self._cached_line_to_code: Dict[Filename, List[bytes]] = {}

        self._working_dir = Path.cwd()
        
        self.compiler_version: str = binary
        

        self._platform = Solc(target, self.compiler_version)

        self._compilation_units: Dict[str, CompilationUnit] = {}

        self.libraries: Optional[Dict[str, int]] = _extract_libraries(kwargs.get("compile_libraries", None))  # type: ignore
        
        
        self._compile(**kwargs)

    @property
    def target(self) -> str:
        """Return the project's target

        Returns:
            str: target
        """
        return self._platform.target

    @property
    def compilation_units(self) -> Dict[str, CompilationUnit]:
        """Return the compilation units

        Returns:
            Dict[str, CompilationUnit]: compilation id => CompilationUnit
        """
        return self._compilation_units

    ###################################################################################
    ###################################################################################
    # region Utils
    ###################################################################################
    ###################################################################################
    @property
    def filenames(self) -> Set[Filename]:
        """
        Return the set of all the filenames used

        Returns:
             Set[Filename]: set of filenames
        """
        filenames: Set[Filename] = set()
        for compile_unit in self._compilation_units.values():
            filenames |= set(compile_unit.filenames)
        return filenames

    def filename_lookup(self, filename: str) -> Filename:
        """Return a crytic_compile.naming.Filename from a any filename

        Args:
            filename (str): filename (used/absolute/relative)

        Raises:
            ValueError: If the filename is not in the project

        Returns:
            Filename: Associated Filename object
        """
        for compile_unit in self.compilation_units.values():
            try:
                return compile_unit.filename_lookup(filename)
            except ValueError:
                pass

        raise ValueError(f"{filename} does not exist")

    @property
    def dependencies(self) -> Set[str]:
        """Return the dependencies files

        Returns:
            Set[str]: Dependencies files
        """
        return self._dependencies

    def is_dependency(self, filename: str) -> bool:
        """Check if the filename is a dependency

        Args:
            filename (str): filename

        Returns:
            bool: True if the filename is a dependency
        """
        return filename in self._dependencies

    @property
    def working_dir(self) -> Path:
        """Return the working directory

        Returns:
            Path: Working directory
        """
        return self._working_dir

    @working_dir.setter
    def working_dir(self, path: Path) -> None:
        """Set the working directory

        Args:
            path (Path): new working directory
        """
        self._working_dir = path

    def _get_cached_offset_to_line(self, file: Filename) -> None:
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

    def get_line_from_offset(self, filename: Union[Filename, str], offset: int) -> Tuple[int, int]:
        """Return the line from a given offset

        Args:
            filename (Union[Filename, str]): filename
            offset (int): global offset

        Returns:
            Tuple[int, int]: (line, line offset)
        """
        if isinstance(filename, str):
            file = self.filename_lookup(filename)
        else:
            file = filename
        if file not in self._cached_offset_to_line:
            self._get_cached_offset_to_line(file)

        lines_delimiters = self._cached_offset_to_line[file]
        return lines_delimiters[offset]

    def _get_cached_line_to_code(self, file: Filename) -> None:
        """Compute the cached lines

        Args:
            file (Filename): filename
        """
        source_code = self.src_content[file.absolute]
        source_code_encoded = source_code.encode("utf-8")
        source_code_list = source_code_encoded.splitlines(True)
        self._cached_line_to_code[file] = source_code_list

    def get_code_from_line(self, filename: Union[Filename, str], line: int) -> Optional[bytes]:
        """Return the code from the line. Start at line = 1.
        Return None if the line is not in the file

        Args:
            filename (Union[Filename, str]): filename
            line (int): line

        Returns:
            Optional[bytes]: line of code
        """
        if isinstance(filename, str):
            file = self.filename_lookup(filename)
        else:
            file = filename
        if file not in self._cached_line_to_code:
            self._get_cached_line_to_code(file)

        lines = self._cached_line_to_code[file]
        if line - 1 < 0 or line - 1 >= len(lines):
            return None
        return lines[line - 1]

    @property
    def src_content(self) -> Dict[str, str]:
        """Return the source content

        Returns:
            Dict[str, str]: filename -> source_code
        """
        # If we have no source code loaded yet, load it for every contract.
        if not self._src_content:
            for filename in self.filenames:
                if filename.absolute not in self._src_content and os.path.isfile(filename.absolute):
                    with open(
                        filename.absolute, encoding="utf8", newline="", errors="replace"
                    ) as source_file:
                        self._src_content[filename.absolute] = source_file.read()
        return self._src_content

    @src_content.setter
    def src_content(self, src: Dict) -> None:
        """Set the source content

        Args:
            src (Dict): New source content
        """
        self._src_content = src

    # endregion
    ###################################################################################
    ###################################################################################
    # region Compile
    ###################################################################################
    ###################################################################################

    def _compile(self, **kwargs: str) -> None:
        """Compile the project

        Args:
            **kwargs: optional arguments. Used: "compile_custom_build", "compile_remove_metadata"
        """

        self._platform.compile(self, **kwargs)

        remove_metadata = kwargs.get("compile_remove_metadata", False)
        if remove_metadata:
            for compilation_unit in self._compilation_units.values():
                for source_unit in compilation_unit.source_units.values():
                    source_unit.remove_metadata()

    # endregion
    ###################################################################################
    ###################################################################################
# target="/Users/sikk/Desktop/Antibug/SafeDevAnalyzer/test/reentrancy.sol"
# instance =AntibugCompile(target)
# print(instance.compilation_units[target].asts)