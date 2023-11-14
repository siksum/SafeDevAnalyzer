"""
Solc platform
"""
import json
import logging
import os
import re
import sys
import shutil
import subprocess
from pathlib import Path
from typing import TYPE_CHECKING, Dict, List, Optional, Union, Any

from antibug.compile.compilation_unit import CompilationUnit
# from antibug.antibug_compile.compiler import CompilerVersion
from antibug.compile.parse_version_and_install_solc import SolcParser
from antibug.compile.exceptions import InvalidCompilation
from antibug.compile.utils.naming import (
    combine_filename_name,
    convert_filename,
    extract_filename,
    extract_name,
)

# Cycle dependency
# from antibug_compile.utils.natspec import Natspec

if TYPE_CHECKING:
    from antibug.compile.antibug_compile import AntibugCompile

LOGGER = logging.getLogger("AntibugCompile")
LOGGER.setLevel(logging.ERROR) 


def _build_contract_data(compilation_unit: "CompilationUnit") -> Dict:
    contracts = {}

    libraries_to_update = compilation_unit.antibug_compile.libraries

    for filename, source_unit in compilation_unit.source_units.items():
        for contract_name in source_unit.contracts_names:
            libraries = source_unit.libraries_names_and_patterns(contract_name)
            abi = str(source_unit.abi(contract_name))
            abi = abi.replace("'", '"')
            abi = abi.replace("True", "true")
            abi = abi.replace("False", "false")
            abi = abi.replace(" ", "")
            exported_name = combine_filename_name(filename.absolute, contract_name)
            contracts[exported_name] = {
                "srcmap": ";".join(source_unit.srcmap_init(contract_name)),
                "srcmap-runtime": ";".join(source_unit.srcmap_runtime(contract_name)),
                "abi": abi,
                "bin": source_unit.bytecode_init(contract_name, libraries_to_update),
                "bin-runtime": source_unit.bytecode_runtime(contract_name, libraries_to_update),
                "userdoc": source_unit.natspec[contract_name].userdoc.export(),
                "devdoc": source_unit.natspec[contract_name].devdoc.export(),
                "libraries": dict(libraries) if libraries else {},
            }
    return contracts


def export_to_solc_from_compilation_unit(
    compilation_unit: "CompilationUnit", key: str, export_dir: str
) -> Optional[str]:
    """Export the compilation unit to the standard solc output format.
    The exported file will be $key.json

    Args:
        compilation_unit (CompilationUnit): Compilation unit to export
        key (str): Filename Id
        export_dir (str): Export directory

    Returns:
        Optional[str]: path to the file generated
    """
    contracts = _build_contract_data(compilation_unit)

    # Create additional informational objects.
    sources = {filename: {"AST": ast} for (filename, ast) in compilation_unit.asts.items()}
    source_list = [x.absolute for x in compilation_unit.filenames]

    # Create our root object to contain the contracts and other information.
    output = {"sources": sources, "sourceList": source_list, "contracts": contracts}

    # If we have an export directory specified, we output the JSON.
    if export_dir:
        if not os.path.exists(export_dir):
            os.makedirs(export_dir)
        path = os.path.join(export_dir, f"{key}.json")

        with open(path, "w", encoding="utf8") as file_desc:
            json.dump(output, file_desc)
        return path
    return None


def export_to_solc(antibug_compile: "AntibugCompile", **kwargs: str) -> List[str]:
    """Export all the compilation units to the standard solc output format.
    The files generated will be either
    - combined_solc.json, if there is one compilation unit (echidna legacy)
    - $key.json, where $key is the compilation unit identifiant

    Args:
        antibug_compile (AntibugCompile): AntibugCompile object to export
        **kwargs: optional arguments. Used: "export_dir"

    Returns:
        List[str]: List of filenames generated
    """
    # Obtain objects to represent each contract
    export_dir = kwargs.get("export_dir", "crytic-export")

    if len(antibug_compile.compilation_units) == 1:
        compilation_unit = list(antibug_compile.compilation_units.values())[0]
        path = export_to_solc_from_compilation_unit(compilation_unit, "combined_solc", export_dir)
        if path:
            return [path]
        return []

    paths = []
    for key, compilation_unit in antibug_compile.compilation_units.items():
        path = export_to_solc_from_compilation_unit(compilation_unit, key, export_dir)
        if path:
            paths.append(path)
    return paths


class Solc():
    """
    Solc platform
    """

    NAME = "solc"
    PROJECT_URL = "https://github.com/ethereum/solidity"
    
    def __init__(self, target: str, binary:str, **kwargs: str):
        self.target = target
        self.compiler_version = binary


    def compile(self, antibug_compile: "AntibugCompile", **kwargs: str) -> None:
        """Run the compilation

        Args:
            antibug_compile (AntibugCompile): Associated AntibugCompile object
            **kwargs: optional arguments. Used: "solc_working_dir", "solc_force_legacy_json"

        Raises:
            InvalidCompilation: If solc failed to run
        """

        solc_working_dir = kwargs.get("solc_working_dir", None)
        force_legacy_json = kwargs.get("solc_force_legacy_json", False)
        compilation_unit = CompilationUnit(antibug_compile, str(self.target), self.compiler_version)

        targets_json = _get_targets_json(compilation_unit, self.target, **kwargs)

        # there have been a couple of changes in solc starting from 0.8.x,
        if force_legacy_json and _is_at_or_above_minor_version(compilation_unit, 8):
            raise InvalidCompilation("legacy JSON not supported from 0.8.x onwards")

        skip_filename = compilation_unit.compiler_version in [
            f"0.4.{x}" for x in range(0, 10)
        ]

        if "sources" in targets_json:
            for path, info in targets_json["sources"].items():
                if skip_filename:
                    path = convert_filename(
                        self.target,
                        relative_to_short,
                        antibug_compile,
                        working_dir=solc_working_dir,
                    )
                else:
                    path = convert_filename(
                        path, relative_to_short, antibug_compile, working_dir=solc_working_dir
                    )
                source_unit = compilation_unit.create_source_unit(path)
                source_unit.ast = info["AST"]

        solc_handle_contracts(
            targets_json, skip_filename, compilation_unit, self.target, solc_working_dir
        )


    @staticmethod
    def is_supported(target: str, **kwargs: str) -> bool:
        """Check if the target is a Solidity file

        Args:
            target (str): path to the target
            **kwargs: optional arguments. Not used

        Returns:
            bool: True if the target is a Solidity file
        """
        return os.path.isfile(target) and target.endswith(".sol")

    def is_dependency(self, _path: str) -> bool:
        """Check if the path is a dependency (always false for direct solc)

        Args:
            _path (str): path to the target

        Returns:
            bool: True if the target is a dependency
        """
        return False


def _get_targets_json(compilation_unit: "CompilationUnit", target: str, **kwargs: Any) -> Dict:
    """Run the compilation, population the compilation info, and returns the json compilation artifacts

    Args:
        compilation_unit (CompilationUnit): Compilation unit
        target (str): path to the solidity file
        **kwargs: optional arguments. Used: "solc", "solc_disable_warnings", "solc_args", "solc_remaps",
            "solc_solcs_bin", "solc_solcs_select", "solc_working_dir", "solc_force_legacy_json"

    Returns:
        Dict: Json of the compilation artifacts
    """
    solc: str = kwargs.get("solc", "solc")
    solc_disable_warnings: bool = kwargs.get("solc_disable_warnings", False)
    solc_arguments: str = kwargs.get("solc_args", "")
    solc_remaps: Optional[Union[str, List[str]]] = kwargs.get("solc_remaps", None)
    # From config file, solcs is a dict (version -> path)
    # From command line, solc is a list
    # The guessing of version only works from config file
    # This is to prevent too complex command line
    solcs_path_: Optional[Union[str, Dict, List[str]]] = kwargs.get("solc_solcs_bin")
    solcs_path: Optional[Union[Dict, List[str]]] = None
    if solcs_path_:
        if isinstance(solcs_path_, str):
            solcs_path = solcs_path_.split(",")
        else:
            solcs_path = solcs_path_
    # solcs_env is always a list. It matches solc-select list
    solc_working_dir = kwargs.get("solc_working_dir", None)
    force_legacy_json = kwargs.get("solc_force_legacy_json", False)

    return _run_solc(
        compilation_unit,
        target,
        solc,
        solc_disable_warnings,
        solc_arguments,
        solc_remaps=solc_remaps,
        working_dir=solc_working_dir,
        force_legacy_json=force_legacy_json,
    )


def solc_handle_contracts(
    targets_json: Dict,
    skip_filename: bool,
    compilation_unit: "CompilationUnit",
    target: str,
    solc_working_dir: Optional[str],
) -> None:
    """Populate the compilation unit from the compilation json artifacts

    Args:
        targets_json (Dict): Compilation artifacts
        skip_filename (bool): If true, skip the filename (for solc <0.4.10)
        compilation_unit (CompilationUnit): Associated compilation unit
        target (str): Path to the target
        solc_working_dir (Optional[str]): Working directory for running solc
    """
    is_above_0_8 = _is_at_or_above_minor_version(compilation_unit, 8)

    if "contracts" in targets_json:

        for original_contract_name, info in targets_json["contracts"].items():
            contract_name = extract_name(original_contract_name)
            # for solc < 0.4.10 we cant retrieve the filename from the ast
            if skip_filename:
                filename = convert_filename(
                    target,
                    relative_to_short,
                    compilation_unit.antibug_compile,
                    working_dir=solc_working_dir,
                )
            else:
                filename = convert_filename(
                    extract_filename(original_contract_name),
                    relative_to_short,
                    compilation_unit.antibug_compile,
                    working_dir=solc_working_dir,
                )

            source_unit = compilation_unit.create_source_unit(filename)

            source_unit.add_contract_name(contract_name)
            compilation_unit.filename_to_contracts[filename].add(contract_name)
            source_unit.abis[contract_name] = (
                json.loads(info["abi"]) if not is_above_0_8 else info["abi"]
            )
            source_unit.bytecodes_init[contract_name] = info["bin"]
            source_unit.bytecodes_runtime[contract_name] = info["bin-runtime"]
            source_unit.srcmaps_init[contract_name] = info["srcmap"].split(";")
            source_unit.srcmaps_runtime[contract_name] = info["srcmap-runtime"].split(";")


def _is_at_or_above_minor_version(compilation_unit: "CompilationUnit", version: int) -> bool:
    """Checks if the solc version is at or above(=newer) a given minor (0.x.0) version

    Args:
        compilation_unit (CompilationUnit): Associated compilation unit
        version (int): version to check

    Returns:
        bool: True if the compilation unit version is above or equal to the provided version
    """
    assert compilation_unit.compiler_version
    return int(compilation_unit.compiler_version.split(".")[1]) >= version


def is_optimized(solc_arguments: Optional[str]) -> bool:
    """Check if optimization are used

    Args:
        solc_arguments (Optional[str]): Solc arguments to check

    Returns:
        bool: True if the optimization are enabled
    """
    if solc_arguments:
        return "--optimize" in solc_arguments
    return False


def _build_options(compiler_version: SolcParser, force_legacy_json: bool) -> str:
    """
    Build the solc command line options
    
    Args:
        compiler_version (CompilerVersion): compiler version
        force_legacy_json (bool): true if the legacy json must be used

    Returns:
        str: options to be passed to the CI
    """
    old_04_versions = [f"0.4.{x}" for x in range(0, 12)]
    # compact-format was introduced in 0.4.12 and made the default in solc 0.8.10
    explicit_compact_format = (
        [f"0.4.{x}" for x in range(12, 27)]
        + [f"0.5.{x}" for x in range(0, 18)]
        + [f"0.6.{x}" for x in range(0, 13)]
        + [f"0.7.{x}" for x in range(0, 7)]
        + [f"0.8.{x}" for x in range(0, 10)]
    )
    assert compiler_version
    if compiler_version in old_04_versions or compiler_version.startswith("0.3"):
        return "abi,asm,ast,bin,bin-runtime,srcmap,srcmap-runtime,userdoc,devdoc"
    if force_legacy_json:
        return "abi,asm,ast,bin,bin-runtime,srcmap,srcmap-runtime,userdoc,devdoc,hashes"
    if compiler_version in explicit_compact_format:
        return "abi,asm,ast,bin,bin-runtime,srcmap,srcmap-runtime,userdoc,devdoc,hashes,compact-format"

    return "abi,asm,ast,bin,bin-runtime,srcmap,srcmap-runtime,userdoc,devdoc,hashes"


# pylint: disable=too-many-arguments,too-many-locals,too-many-branches,too-many-statements
def _run_solc(
    compilation_unit: "CompilationUnit",
    filename: str,
    solc: str,
    solc_disable_warnings: bool,
    solc_arguments: Optional[str],
    solc_remaps: Optional[Union[str, List[str]]] = None,
    env: Optional[Dict] = None,
    working_dir: Optional[Union[Path, str]] = None,
    force_legacy_json: bool = False,
) -> Dict:
    """Run solc.
    Ensure that antibug_compile.compiler_version is set prior calling _run_solc

    Args:
        compilation_unit (CompilationUnit): Associated compilation unit
        filename (str): Solidity file to compile
        solc (str): Solc binary
        solc_disable_warnings (bool): If True, disable solc warnings
        solc_arguments (Optional[str]): Additional solc cli arguments
        solc_remaps (Optional[Union[str, List[str]]], optional): Solc remaps. Can be a string where remap are separated with space, or list of str, or a list of. Defaults to None.
        env (Optional[Dict]): Environement variable when solc is run. Defaults to None.
        working_dir (Optional[Union[Path, str]]): Working directory when solc is run. Defaults to None.
        force_legacy_json (bool): Force to use the legacy json format. Defaults to False.

    Raises:
        InvalidCompilation: If solc failed to run or file is not a solidity file

    Returns:
        Dict: Json compilation artifacts
    """
    
    compiler_version = compilation_unit.compiler_version
    # assert compiler_version
    options = _build_options(compiler_version, force_legacy_json)
    cmd = [solc]
    if solc_remaps:
        if isinstance(solc_remaps, str):
            solc_remaps = solc_remaps.split(" ")
        cmd += solc_remaps
    cmd += [filename, "--combined-json", options]
    if solc_arguments:
        # To parse, we first split the string on each '--'
        solc_args = solc_arguments.split("--")
        # Split each argument on the first space found
        # One solc option may have multiple argument sepparated with ' '
        # For example: --allow-paths /tmp .
        # split() removes the delimiter, so we add it again
        solc_args_ = [("--" + x).split(" ", 1) for x in solc_args if x]
        # Flat the list of list
        solc_args = [item.strip() for sublist in solc_args_ for item in sublist if item]
        cmd += solc_args

    try:
        LOGGER.info(
            "'%s' running",
            " ".join(cmd),
        )

        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            executable=shutil.which(cmd[0]),
            # **additional_kwargs,
        )
    except OSError as error:
        # pylint: disable=raise-missing-from
        raise InvalidCompilation(error)
    stdout_, stderr_ = process.communicate()
    stdout, stderr = (
        stdout_.decode(encoding="utf-8", errors="ignore"),
        stderr_.decode(encoding="utf-8", errors="ignore"),
    )  # convert bytestrings to unicode strings

    if stderr and (not solc_disable_warnings):
        LOGGER.error(stderr)
        sys.exit(1)
        
    try:
        ret: Dict = json.loads(stdout)
        return ret
    except json.decoder.JSONDecodeError:
        # pylint: disable=raise-missing-from
        raise InvalidCompilation(f"Invalid solc compilation {stderr}")



PATTERN = re.compile(r"pragma solidity\s*(?:\^|>=|<=)?\s*(\d+\.\d+\.\d+)")


def relative_to_short(relative: Path) -> Path:
    """Convert relative to short (does nothing for direct solc)

    Args:
        relative (Path): target

    Returns:
        Path: Converted path
    """
    return relative

