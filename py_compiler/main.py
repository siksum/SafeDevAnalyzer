from pathlib import Path
from typing import Any, Dict, List, Optional, Union
from semantic_version import Version

from parse_version_and_install_solc import *


def execute_solc(source: str, 
            solc_binary_path: Union[Path, str] = None,
            solc_version: Union[Version, str] = None,
            output_values: Optional[List] = None):
    solc_binary_path = solc_binary_path.joinpath(f"solc-{solc_version}")
    print("solc_binary_path: ", solc_binary_path)
    command: List = [str(solc_binary_path)]

    if isinstance(source, (str, Path)):
        command.append(source)
    
    option = ["--combined-json", "bin,abi"]
    command.extend(option)
    print("command: ", command)

    

    proc = subprocess.Popen(
        command,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        encoding="utf8",
    )

    stdoutdata, stderrdata = proc.communicate()
    print("stdout: ", stdoutdata)
    print("stderr: ", stderrdata)


def main():
    solidity_file, solc_version, solc_binary_path = parser_main(sys.argv[1])
    execute_solc(solidity_file, solc_binary_path, solc_version)


if __name__ == "__main__":
    main()