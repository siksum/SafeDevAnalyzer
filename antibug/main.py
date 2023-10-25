from antibug.antibug_compile.compile import SafeDevAnalyzer

import sys
import json
import os

def get_root_dir():
    current_working_directory = os.getcwd()
    while not os.path.basename(current_working_directory) == "SafeDevAnalyzer":
        current_working_directory = os.path.dirname(current_working_directory)
    return current_working_directory


def convert_to_json(abi_list, bytecode_list, analyzer:SafeDevAnalyzer):
    combined_data = {}

    output_dir = os.path.join(get_root_dir(), "json_results")
    print(output_dir)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    for abi, bytecode, filename in zip(abi_list, bytecode_list, analyzer.target_list):
        filename=os.path.basename(filename)[:-4]
        key = next(iter(abi))
        combined_data[key] = {
            "contract": key,
            "abis": abi[key],
            "bytecodes": "0x" + bytecode[key]
        }
        combined_json = json.dumps(combined_data[key], indent=2)
        try:
            output_path = os.path.join(output_dir+f"/{filename}.json")
            with open(output_path, "w") as f:
                f.write(combined_json)
        except Exception as e:
            print(f"Failed to write to {output_path}. Reason: {e}")

def main():
    analyzer = SafeDevAnalyzer(sys.argv[1])
    abi_list, bytecode_list = analyzer.to_deploy()
    convert_to_json(abi_list, bytecode_list, analyzer)
if __name__ == "__main__":
    main()
