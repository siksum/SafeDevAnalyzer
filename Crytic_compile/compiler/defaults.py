"""
Default value for options
"""


# Those are the flags shared by the command line and the config file
DEFAULTS_FLAG_IN_CONFIG = {
    "compile_force_framework": None,
    "compile_remove_metadata": False,
    "compile_custom_build": None,
    "solc": "solc",
    "solc_remaps": None,
    "solc_args": None,
    "solc_disable_warnings": False,
    "solc_working_dir": None,
    "solc_solcs_select": None,
    "solc_solcs_bin": None,
    "solc_standard_json": False,
    "solc_force_legacy_json": False,
    "npx_disable": False,
    "ignore_compile": False,
    "skip_clean": False,
    "export_dir": "crytic-export",
    "compile_libraries": None,
}
