from pathlib import Path
from typing import Any, Dict, List, Optional, Union
from semantic_version import Version

from parse_version_and_install_solc import *
from exceptions import *


def execute_solc(source: str, 
            solc_binary_path: Union[Path, str] = None,
            solc_version: Union[Version, str] = None):
    
    solc_binary_path = solc_binary_path.joinpath(f"solc-{solc_version}")

    command: List = [str(solc_binary_path)]

    if isinstance(source, (str, Path)):
        command.append(source)
    
    option = ["--combined-json", "bin,abi,ast"]
    command.extend(option)
    
    proc = subprocess.Popen(
        command,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        encoding="utf8",
    )

    stdout, stderr = proc.communicate()
   
    if stderr:
        print("solc stderr:\n%s", stderr) 

    try:
        ret: Dict = json.loads(stdout)
        return ret
    except json.decoder.JSONDecodeError:
        raise InvalidCompilation(f"Invalid solc compilation {stderr}")


def main():
    solidity_file, solc_version, solc_binary_path = parser_main(sys.argv[1])
    ret = execute_solc(solidity_file, solc_binary_path, solc_version)
    print(ret)

if __name__ == "__main__":
    main()