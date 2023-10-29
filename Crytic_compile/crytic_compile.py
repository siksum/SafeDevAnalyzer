"""
CryticCompile main module. Handle the compilation.
"""

import logging
import os
from collections import defaultdict
from pathlib import Path
from typing import TYPE_CHECKING, Dict, List, Optional, Set, Tuple, Union

from Crytic_compile.compilation_unit import CompilationUnit

from solc import Solc
from Crytic_compile.naming import Filename

# Cycle dependency
if TYPE_CHECKING:
    pass

LOGGER = logging.getLogger("CryticCompile")
logging.basicConfig()


# pylint: disable=too-many-instance-attributes
class CryticCompile:

    # pylint: disable=too-many-branches
    def __init__(self, target: Union[str, Solc], **kwargs: str) -> None:

        self._src_content: Dict = {}

        self._cached_offset_to_line: Dict[Filename, Dict[int, Tuple[int, int]]] = {}
        # Lines are indexed from 1
        self._cached_line_to_offset: Dict[Filename, Dict[int, int]] = defaultdict(dict)

        # Return the line from the line number
        # Note: line 1 is at index 0
        self._cached_line_to_code: Dict[Filename, List[bytes]] = {}
        self._working_dir = Path.cwd()
        self._platform = Solc(target)
        self._compilation_units: Dict[str, CompilationUnit] = {}
        self._bytecode_only = False
        self._platform.compile(self, **kwargs)

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

    def is_in_multiple_compilation_unit(self, contract: str) -> bool:
        """Check if the contract is shared by multiple compilation unit

        Args:
            contract (str): contract name

        Returns:
            bool: True if the contract is in multiple compilation units
        """
        count = 0
        for compilation_unit in self._compilation_units.values():
            for source_unit in compilation_unit.source_units.values():
                if contract in source_unit.contracts_names:
                    count += 1
        return count >= 2

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

    def src_content_for_file(self, filename_absolute: str) -> Optional[str]:
        """Get the source code of the file

        Args:
            filename_absolute (str): absolute filename

        Returns:
            Optional[str]: source code
        """
        return self.src_content.get(filename_absolute, None)

    # endregion
    ###################################################################################
    ###################################################################################
   
    # region Compiler information
    ###################################################################################
    ###################################################################################

    @property
    def bytecode_only(self) -> bool:
        """Return true if only the bytecode was retrieved.
        This can only happen for the etherscan platform

        Returns:
            bool: True if the project is bytecode only
        """
        return self._bytecode_only

    @bytecode_only.setter
    def bytecode_only(self, bytecode: bool) -> None:
        """Set the bytecode_only info (only for etherscan)

        Args:
            bytecode (bool): new bytecode_only status
        """
        self._bytecode_only = bytecode

    # endregion
    ###################################################################################
    ###################################################################################