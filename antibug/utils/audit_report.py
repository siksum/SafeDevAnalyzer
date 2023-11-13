from antibug.utils.convert_to_json import output_dir, get_output_path
import os
from typing import Optional
import json


def write_to_markdown(output_dir_path, combined_json, target: Optional[str] = None):
    if target is not None:      
        output_path= get_output_path(target, output_dir_path, "md")

    try:
        with open(output_path, "w") as f:
            f.write(combined_json)
    except Exception as e:
        print(f"Failed to write to {output_path}. Reason: {e}")
        

def export_to_markdown(filename):
    output_dir_path = output_dir("audit_report")
    json_path = get_output_path(filename, os.path.join(os.path.dirname(output_dir_path),"detector_json_results"), "json")
    with open(json_path, "r") as file:
        json_str = file.read()
        json_data = json.loads(json_str)
        
    extracted_data = []
    for result in json_data['results']:
        for element in result['elements']:
            element_data = {
                'type': element['type'],
                'name': element['name']
            }
            if 'type_specific_fields' in element and 'parent' in element['type_specific_fields']:
                parent = element['type_specific_fields']['parent']
                element_data['parent_type'] = parent.get('type', None)
                element_data['parent_name'] = parent.get('name', None)
            extracted_data.append(element_data)
    
    # 추출된 데이터 출력
    for item in extracted_data:
        print(item)
       
    #         if json_data['filename_absolute']:
    #             filename = json_data['filename_absolute']
    # print(filename)
                
                

    
    # with open(os.path.join(output_dir_path, "audit_report.md"), "w") as f:
    #     f.write("# Audit Report\n\n")
    #     for result, filename, error in zip(result_list, filename_list, error_list):
    #         if error is not None:
    #             f.write(f"## {filename}\n\n")
    #             f.write(f"### Error\n\n")
    #             f.write(f"{error}\n\n")
    #         else:
    #             f.write(f"## {filename}\n\n")
    #             f.write(f"### Results\n\n")
    #             f.write(f"{result}\n\n")


