"""
Module containing all the supported export functions
"""
from Crytic_compile.solc_compile.solc import export_to_solc

PLATFORMS_EXPORT = {
    "solc": export_to_solc,
}
