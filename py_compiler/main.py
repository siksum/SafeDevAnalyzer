from pathlib import Path
from typing import Any, Dict, List, Optional, Union
from semantic_version import Version

from parse_version_and_install_solc import *


def compile(source: str, 
            solc_binary: Union[Path, str] = None,
            solc_version: Union[Version, str] = None,
            output_values: Optional[List] = None):
    print("compile")


def main():
    solidity_file, version, solc_version, solc_binary_path = parser_main(sys.argv[1])
    print("sol: \n", solidity_file)
    print("sol version: ",version)
    print("solc version: ", solc_version)
    print("solc path: ", solc_binary_path)

    cmd = f"solc {sys.argv[1]} --combined-json abi,asm,ast,opcodes"
    subprocess.call(cmd, shell=True)


if __name__ == "__main__":
    main()