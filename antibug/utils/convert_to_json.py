import glob
import json
import os
import shutil
from typing import Optional
from antibug.compile.safe_dev_analyzer import SafeDevAnalyzer


def get_root_dir():
    current_path = os.path.dirname(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
    return current_path


def output_dir(filename):
    output_dir = os.path.join(get_root_dir(), f"result/{filename}")
    files = glob.glob(os.path.join(output_dir, "*"))
    for f in files:
        try:
            os.remove(f)
        except Exception as e:
            print(f"Failed to delete {f}. Reason: {e}")

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    return output_dir


def print_output_dir(output_dir_path, language_type):
    if language_type == "json":
        print(f"Detect Result Output directory: {output_dir_path}")
    elif language_type == "md":
        print(f"Audit Report Output directory: {output_dir_path}")
    elif language_type == "compile":
        print(f"Compile Info Output directory: {output_dir_path}")
    elif language_type == "analysis":
        print(f"Contract Analysis Info Output directory: {output_dir_path}")


def get_output_path(target, output_dir_path, language, language_type):
    filename=os.path.basename(target)[:-4]
    if language == "korean":
        if language_type == "json":
            output_path = os.path.join(output_dir_path, f"{filename}_kr.json")
        elif language_type == "md":
            output_path = os.path.join(output_dir_path, f"{filename}_kr.md")
    elif language == "english":
        if language_type == "json":
            output_path = os.path.join(output_dir_path, f"{filename}_en.json")
        elif language_type == "md":
            output_path = os.path.join(output_dir_path, f"{filename}_en.md")
    else:
        output_path = os.path.join(output_dir_path, f"{filename}.json")
    return output_path


def write_to_json(output_dir_path, combined_json, language, filename: Optional[str] = None):
    if filename is not None:      
        output_path= get_output_path(filename, output_dir_path, language, "json")
    try:
        with open(output_path, "w") as f:
            f.write(combined_json)
    except Exception as e:
        print(f"Failed to write to {output_path}. Reason: {e}")
        
        
def read_to_json(json_path):
    with open(json_path, "r") as file:
        json_str = file.read()
        json_data = json.loads(json_str)
    return json_data


def convert_to_compile_info_json(abi_list, bytecode_list, analyzer: SafeDevAnalyzer):
    output_dir_path = output_dir("compile_json_results")
    language = "compile"
    
    for abi, bytecode, filename in zip(abi_list, bytecode_list, analyzer.file_list):
        combined_data = {}
        for (contract, abi_data), bytecode_data in zip(abi.items(), bytecode.values()):
            combined_data[contract] = {
                "abis": abi_data,
                "bytecodes": "0x" + bytecode_data
            }
            result_json = json.dumps(combined_data, indent=2)
            write_to_json(output_dir_path, result_json, language, filename)
    print("Output Directory:",os.path.dirname(output_dir_path))



def convert_to_detect_result_json(result_list, filename, error, safe_dev_analyzer:"SafeDevAnalyzer") -> None:
    output_dir_path = output_dir("detector_json_results")
    combined_data_list = [] 
    json_result = {}  
    result_list = [item for item in result_list if item is not None and item != '' and item != []]

    if len(result_list) == 0:
        print("Nothing to detect")
        return 0   
    for language in ["korean", "english"]:
        for result in result_list:
            for data in result:
                combined_data = {}
                combined_data['filename'] = data["elements"][0]["source_mapping"]["filename_absolute"]
                combined_data['detector'] = data["check"]
                combined_data['impact'] = data["impact"]
                combined_data['confidence'] = data["confidence"]
                combined_data['element'] = []
                
                for element in data["elements"]:
                    source_mapping = safe_dev_analyzer.antibug_compile[0].get_code_from_line(safe_dev_analyzer.file_path, element['source_mapping']['lines'][0])
                    element_data = {
                        'type': element['type'],
                        'name': element['name'],
                        'line': element['source_mapping']['lines'][0],
                        'code': source_mapping.decode("utf-8"),
                    }
                    if "type_specific_fields" in element and "parent" in element["type_specific_fields"]:
                        parent = element["type_specific_fields"]["parent"]
                        element_data["parent_type"] = parent.get("type", None)
                        element_data["parent_name"] = parent.get("name", None)
                    
                    combined_data['element'].append(element_data)
                    
                combined_data['info'] = data["info"]
                combined_data['description'] = data["description"]
                combined_data['exploit_scenario'] = data["exploit_scenario"]
                combined_data['recommendation'] = data["recommendation"]
                
                combined_data['info_korean'] = data["info_korean"]
                combined_data['description_korean'] = data["description_korean"]
                combined_data['exploit_scenario_korean'] = data["exploit_scenario_korean"]
                combined_data['recommendation_korean'] = data["recommendation_korean"]
                
                combined_data['reference'] = data["reference"]
                            
                if language == "korean":
                    del combined_data["info"]
                    del combined_data["description"]
                    del combined_data["exploit_scenario"]
                    del combined_data["recommendation"]
                        
                elif language == "english":
                    del combined_data["info_korean"]
                    del combined_data["description_korean"]
                    del combined_data["exploit_scenario_korean"]
                    del combined_data["recommendation_korean"]
                combined_data_list.append(combined_data)
        
        for combined_data in combined_data_list:
            json_result[combined_data["detector"]] = {"success": error is None, "error": error, "results": combined_data}
            combined_json = json.dumps(json_result, indent=2, ensure_ascii=False)
            write_to_json(output_dir_path, combined_json, language, filename)


def convert_to_contract_analysis_info_json(combined_json_list, safe_dev_analyzer:"SafeDevAnalyzer"):
    output_dir_path = output_dir("contract_analysis_json_results")
    json_result = {}
    for combined_data in combined_json_list:
        json_result[combined_data["Contract Name"]] = combined_data    
        combined_json = json.dumps(json_result, indent=2)
        write_to_json(output_dir_path, combined_json, "analysis", safe_dev_analyzer.file_basename)
    print("Output Directory:", os.path.dirname(output_dir_path))


def remove_all_json_files():
    output_dir = os.path.join(get_root_dir(), f"result")
    try:
        shutil.rmtree(output_dir)
    except Exception as e:
        print(f"ERROR: {e}")
    