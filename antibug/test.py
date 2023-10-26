from antibug_compile.compile import SafeDevAnalyzer
import sys
import os
import glob
import json

def get_root_dir():
    current_path = os.path.dirname(os.path.abspath(os.path.dirname(__file__)))
    print(current_path)
    return current_path

def convert_to_json(abi_list, bytecode_list, analyzer:SafeDevAnalyzer):
    combined_data = {}

    output_dir = os.path.join(get_root_dir(), "json_results")
    print(f"Output directory: {output_dir}")

    # Delete all files inside the output directory
    files = glob.glob(os.path.join(output_dir, "*"))
    for f in files:
        try:
            os.remove(f)
        except Exception as e:
            print(f"Failed to delete {f}. Reason: {e}")

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
            print(f"Successfully wrote to {output_path}")
        except Exception as e:
            print(f"Failed to write to {output_path}. Reason: {e}")

analyzer = SafeDevAnalyzer(sys.argv[1])
#get_root_dir()
abi_list, bytecode_list = analyzer.to_deploy()
print("abi and bytecode")
convert_to_json(abi_list, bytecode_list, analyzer)