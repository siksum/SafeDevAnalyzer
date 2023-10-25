"""
Module containing all the supported export functions
"""
from Crytic_compile.platforms.archive import export_to_archive
from Crytic_compile.platforms.solc import export_to_solc
from Crytic_compile.platforms.standard import export_to_standard
from Crytic_compile.platforms.truffle import export_to_truffle

PLATFORMS_EXPORT = {
    "standard": export_to_standard,
    "crytic-compile": export_to_standard,
    "solc": export_to_solc,
    "truffle": export_to_truffle,
    "archive": export_to_archive,
}
