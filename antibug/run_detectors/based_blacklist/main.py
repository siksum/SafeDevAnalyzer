#!/usr/bin/env python3

import argparse
import logging
import sys
import json

from Crytic_compile import cryticparser

from antibug.run_detectors.based_blacklist.test import test
from antibug.run_detectors.based_blacklist.vuln import vuln

logger = logging.getLogger("detector")


logging.basicConfig()

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="smart contract vulnability detector based blacklist"
    )

    parser.add_argument("model", help="model.bin")

    parser.add_argument("--filename", action="store", dest="filename", help="contract.sol")

    parser.add_argument("--fname", action="store", dest="fname", help="Target function")


    parser.add_argument(
        "--input", action="store", dest="input", help="File or directory used as input"
    )

    parser.add_argument(
        "--ntop",
        action="store",
        type=int,
        dest="ntop",
        default=10,
        help="Number of more similar contracts to show for testing",
    )


    cryticparser.init(parser)

    if len(sys.argv) == 1:
        parser.print_help(sys.stderr)
        sys.exit(1)
    
    args = parser.parse_args()
    return args


def main() -> None:
    args = parse_args()
    filename, contract, fname, res = test(args)

    target_info = {
        # "model" : model,
        "filename" : filename,
        "contract" : contract,
        "fname" : fname
    }

    similarity = []

    for key, value in res.items():
        path, contract, function = key
        score = float(value)
        if score >= 0.9:
            vuln_type, severity = vuln(path)
            with open(path, "r") as code_files:
                code_content = "```solidity\n" + code_files.read() + "```"
            entry = {
                "vulneability_type" : vuln_type,
                "severity" : severity,
                "path" : path,
                "code" : code_content,
                "contract" : contract,
                "function" : function,
                "score" : score
            }
            similarity.append(entry)
    
    result = {
        "target" : [target_info],
        "similarity" : similarity
    }
    
    with open(f"{contract}_{fname}.json", "w") as json_file:
        json.dump(result, json_file, indent=2)
    


if __name__ == "__main__":
    main()