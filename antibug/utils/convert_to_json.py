import glob
import json
import os

from typing import Optional, Dict

from antibug.compile.safe_dev_analyzer import SafeDevAnalyzer


def get_root_dir():
    current_path = os.path.dirname(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
    return current_path

def output_dir(filename):
    output_dir = os.path.join(get_root_dir(), f"result/{filename}")
    print(f"Output directory: {output_dir}")

    files = glob.glob(os.path.join(output_dir, "*"))
    for f in files:
        try:
            os.remove(f)
        except Exception as e:
            print(f"Failed to delete {f}. Reason: {e}")

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    return output_dir

def get_output_path(target, output_dir_path):
    filename=os.path.basename(target)[:-4]
    output_path = os.path.join(output_dir_path, f"{filename}.json")
    return output_path

def write_to_json(output_dir_path, combined_json, target: Optional[str] = None):
    if target is not None:      
        output_path= get_output_path(target, output_dir_path)

    try:
        with open(output_path, "w") as f:
            f.write(combined_json)
    except Exception as e:
        print(f"Failed to write to {output_path}. Reason: {e}")


def convert_to_deploy_info_json(abi_list, bytecode_list, analyzer: SafeDevAnalyzer):
    output_dir_path = output_dir("deploy_json_results")
    
    for abi, bytecode, filename in zip(abi_list, bytecode_list, analyzer.target_list):
        combined_data = {}
        for (contract, abi_data), bytecode_data in zip(abi.items(), bytecode.values()):
            combined_data[contract] = {
                "abis": abi_data,
                "bytecodes": "0x" + bytecode_data
            }
            result_json = json.dumps(combined_data, indent=2)
            write_to_json(output_dir_path, result_json, filename)



def convert_to_detect_result_json(result_list, filename_list, error_list) -> None:
    output_dir_path = output_dir("basic_detector_json_results")
    
    for result, filename, error in zip(result_list, filename_list, error_list):
        json_result = {"success": error is None, "error": error, "results": result}
        combined_json = json.dumps(json_result, indent=2)

        write_to_json(output_dir_path, combined_json, filename)


def convert_to_blacklist_result_json(result, contract, function):
    output_dir_path = output_dir("blacklist_json_results")
    combined_json = json.dumps(result, indent=2)
    output_path = os.path.join(output_dir_path, f"{contract}_{function}.json")
    
    write_to_json(output_path, combined_json)


