"""
Module handling the cli arguments

Call cryticparser.init(parser: ArgumentParser) to setup all the crytic-compile arguments in the argument parser
"""
from argparse import ArgumentParser

from Crytic_compile.cryticparser import DEFAULTS_FLAG_IN_CONFIG


def init(parser: ArgumentParser) -> None:
    """Add crytic-compile arguments to the parser

    Args:
        parser (ArgumentParser): argparser where the cli flags are added
    """


    _init_solc(parser)



def _init_solc(parser: ArgumentParser) -> None:
    """Init solc arguments

    Args:
        parser (ArgumentParser): argparser where the cli flags are added
    """

    group_solc = parser.add_argument_group("Solc options")
    group_solc.add_argument(
        "--solc", help="solc path", action="store", default=DEFAULTS_FLAG_IN_CONFIG["solc"]
    )

    group_solc.add_argument(
        "--solc-remaps",
        help="Add remapping",
        action="store",
        default=DEFAULTS_FLAG_IN_CONFIG["solc_remaps"],
    )

    group_solc.add_argument(
        "--solc-args",
        help="Add custom solc arguments. Example: --solc-args"
        ' "--allow-path /tmp --evm-version byzantium".',
        action="store",
        default=DEFAULTS_FLAG_IN_CONFIG["solc_args"],
    )

    group_solc.add_argument(
        "--solc-disable-warnings",
        help="Disable solc warnings",
        action="store_true",
        default=DEFAULTS_FLAG_IN_CONFIG["solc_disable_warnings"],
    )

    group_solc.add_argument(
        "--solc-working-dir",
        help="Change the default working directory",
        action="store",
        default=DEFAULTS_FLAG_IN_CONFIG["solc_working_dir"],
    )

    group_solc.add_argument(
        "--solc-solcs-select",
        help="Specify different solc version to try (env config). Depends on solc-select    ",
        action="store",
        default=DEFAULTS_FLAG_IN_CONFIG["solc_solcs_select"],
    )

    group_solc.add_argument(
        "--solc-solcs-bin",
        help="Specify different solc version to try (path config)."
        " Example: --solc-solcs-bin solc-0.4.24,solc-0.5.3",
        action="store",
        default=DEFAULTS_FLAG_IN_CONFIG["solc_solcs_bin"],
    )

    group_solc.add_argument(
        "--solc-standard-json",
        help="Compile all specified targets in a single compilation using solc standard json",
        action="store_true",
        default=DEFAULTS_FLAG_IN_CONFIG["solc_standard_json"],
    )

    group_solc.add_argument(
        "--solc-force-legacy-json",
        help="Force the solc compiler to use the legacy json ast format over the compact json ast format",
        action="store_true",
        default=DEFAULTS_FLAG_IN_CONFIG["solc_force_legacy_json"],
    )