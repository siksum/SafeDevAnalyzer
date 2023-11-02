"""
Solc platform
"""
import json
import logging
import os
import re
import shutil
import subprocess
from pathlib import Path
from typing import TYPE_CHECKING, Dict, List, Optional, Union, Any

from Crytic_compile.compilation_unit import CompilationUnit
from Crytic_compile.exceptions import InvalidCompilation
from Crytic_compile.naming import (
    combine_filename_name,
    convert_filename,
    extract_filename,
    extract_name,
)

from antibug.antibug_compile.parse_version_and_install_solc import SolcParser

# Cycle dependency
if TYPE_CHECKING:
    from Crytic_compile import CryticCompile

LOGGER = logging.getLogger("CryticCompile")

class Solc():

    NAME = "solc"
    PROJECT_URL = "https://github.com/ethereum/solidity"

    def __init__(self, target: str, **kwargs: str):
        self.target = target

    def compile(self, crytic_compile: "CryticCompile", **kwargs: str) -> None:
        solc_working_dir = kwargs.get("solc_working_dir", None)
        compilation_unit = CompilationUnit(crytic_compile, str(self.target))

        targets_json = _get_targets_json(compilation_unit, self.target, **kwargs)

        if "sources" in targets_json:
            for path, info in targets_json["sources"].items():
                path = convert_filename(
                    path, relative_to_short, crytic_compile, working_dir=solc_working_dir
                )
                source_unit = compilation_unit.create_source_unit(path)
                source_unit.ast = info["AST"]

        solc_handle_contracts(
            targets_json, compilation_unit, solc_working_dir
        )


    # def is_dependency(self, _path: str) -> bool:
    #     """Check if the path is a dependency (always false for direct solc)

    #     Args:
    #         _path (str): path to the target

    #     Returns:
    #         bool: True if the target is a dependency
    #     """
    #     return False

def _get_targets_json(compilation_unit: "CompilationUnit", target: str, **kwargs: Any) -> Dict:
    solc: str = kwargs.get("solc", "solc")
    solc_disable_warnings: bool = kwargs.get("solc_disable_warnings", False)
    solc_remaps: Optional[Union[str, List[str]]] = kwargs.get("solc_remaps", None)

    return _run_solc(
        compilation_unit,
        target,
        solc,
        solc_disable_warnings,
        solc_remaps=solc_remaps,
    )

def solc_handle_contracts(
    targets_json: Dict,
    compilation_unit: "CompilationUnit",
    solc_working_dir: Optional[str],
) -> None:

    if "contracts" in targets_json:
        for original_contract_name, info in targets_json["contracts"].items():
            contract_name = extract_name(original_contract_name)

            filename = convert_filename(
                extract_filename(original_contract_name),
                relative_to_short,
                compilation_unit.crytic_compile,
                working_dir=solc_working_dir,
            )

            source_unit = compilation_unit.create_source_unit(filename)
            source_unit.add_contract_name(contract_name)
            compilation_unit.filename_to_contracts[filename].add(contract_name)
            source_unit.abis[contract_name] = info["abi"]
            source_unit.bytecodes_init[contract_name] = info["bin"]
            source_unit.bytecodes_runtime[contract_name] = info["bin-runtime"]


def _build_options(compiler_version: SolcParser) -> str:
    old_04_versions = [f"0.4.{x}" for x in range(0, 12)]
    # compact-format was introduced in 0.4.12 and made the default in solc 0.8.10
    explicit_compact_format = (
        [f"0.4.{x}" for x in range(13, 27)]
        + [f"0.5.{x}" for x in range(0, 18)]
        + [f"0.6.{x}" for x in range(0, 13)]
        + [f"0.7.{x}" for x in range(0, 7)]
        + [f"0.8.{x}" for x in range(0, 10)]
    )
    assert compiler_version.version
    if compiler_version.version in old_04_versions or compiler_version.version[0].startswith("0.3"):
        return "abi,ast,bin,bin-runtime,srcmap,srcmap-runtime,userdoc,devdoc"
    if compiler_version.version in explicit_compact_format:
        return "abi,ast,bin,bin-runtime,srcmap,srcmap-runtime,userdoc,devdoc,hashes,compact-format"

    return "abi,ast,bin,bin-runtime,srcmap,srcmap-runtime,userdoc,devdoc,hashes"


# pylint: disable=too-many-arguments,too-many-locals,too-many-branches,too-many-statements
def _run_solc(
    compilation_unit: "CompilationUnit",
    filename: str,
    solc: str,
    solc_disable_warnings: bool,
    solc_remaps: Optional[Union[str, List[str]]] = None,
) -> Dict:


    compilation_unit.compiler_version = SolcParser(filename)
    compiler_version = compilation_unit.compiler_version

    #assert compiler_version
    options = _build_options(compiler_version)

    cmd = [solc]
    if solc_remaps:
        if isinstance(solc_remaps, str):
            solc_remaps = solc_remaps.split(" ")
        cmd += solc_remaps
    cmd += [filename, "--combined-json", options]

    try:
        LOGGER.info(
            "'%s' running",
            " ".join(cmd),
        )
        # pylint: disable=consider-using-with

        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            executable=shutil.which(cmd[0]),
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
        LOGGER.info("Compilation warnings/errors on %s:\n%s", filename, stderr)

    try:
        ret: Dict = json.loads(stdout)
        return ret
    except json.decoder.JSONDecodeError:
        # pylint: disable=raise-missing-from
        raise InvalidCompilation(f"Invalid solc compilation {stderr}")

def relative_to_short(relative: Path) -> Path:
    """Convert relative to short (does nothing for direct solc)

    Args:
        relative (Path): target

    Returns:
        Path: Converted path
    """
    return relative
