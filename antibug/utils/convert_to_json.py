import glob
import json
import os

from typing import Optional

from antibug.antibug_compile.compile import SafeDevAnalyzer

def get_root_dir():
    current_path = os.path.dirname(os.path.abspath(os.path.dirname(__file__)))
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


def convert_to_deploy_info_json(abi_list, bytecode_list, analyzer:SafeDevAnalyzer):
    combined_data = {}
    output_dir_path = output_dir("deploy_json_results")
    combined_json = {}
    for (contract, abi_data), bytecode in zip(abi_list[0].items(), bytecode_list[0].values()):
        combined_data[contract]= {
            "abis": abi_data,
            "bytecodes": "0x" + bytecode
        }
        combined_json=combined_data
    result_json = json.dumps(combined_json, indent=2)   

    write_to_json(output_dir_path, result_json, analyzer.target_list[0])


def convert_to_detect_result_json(result, target):
    output_dir_path = output_dir("basic_detector_json_results")
    combined_json = json.dumps(result, indent=2)

    write_to_json(output_dir_path, combined_json, target)


def convert_to_blacklist_result_json(result, contract, function):
    output_dir_path = output_dir("blacklist_json_results")
    combined_json = json.dumps(result, indent=2)
    output_path = os.path.join(output_dir_path, f"{contract}_{function}.json")
    
    write_to_json(output_path, combined_json)


