import os
import json

from typing import Optional
from antibug.utils.convert_to_json import output_dir, get_output_path, print_output_dir


def write_to_markdown(output_dir_path, payload, target: Optional[str] = None):
    if target is not None:      
        output_path= get_output_path(target, output_dir_path, "md")
        print_output_dir(output_dir_path, "md")
    try:
        with open(output_path, "w") as f:
            f.write(payload)
    except Exception as e:
        print(f"Failed to write to {output_path}. Reason: {e}")
      
def convert_color_to_markdown(level):
    if level == "High":
        return "<span style='color:lightcoral'> High </span>"
    elif level == "Medium":
        return "<span style='color:olivedrab'> Medium </span>"
    elif level == "Low":
        return "<span style='color:sandybrown'> Low </span>"
    elif level == "Informational":
        return "<span style='color:skyblue'> Informational </span>"
    else:
        return level     
        
def export_to_markdown(filename, language):
    output_dir_path = output_dir("audit_report")
    json_path = get_output_path(filename, os.path.join(os.path.dirname(output_dir_path), "detector_json_results"), "json")
    
    try:
        with open(json_path, "r") as file:
            json_str = file.read()
            json_data = json.loads(json_str)
    except Exception as e:
        print(f"Failed to read {json_path}. Reason: {e}")
        
    
    payload = f"# Audit Report\n\n"
    payload += f"> 🔍 `Filename`: {filename}\n"
    payload += "---\n\n"
    
    for detector_type, detector_data in json_data.items(): 
        detector = detector_data["results"]["detector"]
        impact = convert_color_to_markdown(detector_data["results"]["impact"])
        confidence = convert_color_to_markdown(detector_data["results"]["confidence"])
        
        # if confidence  == "High":
        #     confidence = "<span style='color:red'> High </span>"
        # elif confidence == "Medium":
        #     confidence = "<span style='color:green'> Medium </span>"
        # elif confidence == "Low":
        #     confidence = "<span style='color:yellow'> Low </span>"
        # elif confidence == "Informational":
        #     confidence = "<span style='color:blue'> Informational </span>"
        reference = detector_data["results"]["reference"]
        line = detector_data["results"]["element"][-1]["line"]
        code = detector_data["results"]["element"][-1]["code"]
        
        if language == "english":
            description = detector_data["results"]["info"]
            exploit_scenario = detector_data["results"]["exploit_scenario"]
            recommendation = detector_data["results"]["recommendation"]
            info = detector_data["results"]["description"]
        else:
            exploit_scenario = detector_data["results"]["exploit_scenario_korean"]
            recommendation = detector_data["results"]["recommendation_korean"]
            description = detector_data["results"]["info_korean"]
            info = detector_data["results"]["description_korean"]
        
        payload += f"<details>\n"
        payload += f"<summary style='font-size: 20px;'>{detector}</summary>\n"
        payload += f"<div markdown='1'>\n\n"

        payload += f"## Detect Results\n\n"
        payload += f"| Detector | Impact | Confidence | Info |\n"
        payload += f"|:---:|:---:|:---:|:---:|\n"
        payload += f"| {detector} | {impact} | {confidence} | {description} |||\n\n\n"
        
        payload += f"## Vulnerabiltiy in code:\n\n"
        # payload += f"```solidity\n"
        # payload += f"line {line}: {code}\n"
        # payload += f"```\n"
        # payload += f" ---\n\n"
        for code in detector_data['results']['element']:
            payload += f"```solidity\n"
            payload += f"line {code['line']}: {code['code']}\n"
            payload += f"```\n"
            payload += f" ---\n\n "
            
        payload += f"{info}\n\n"
        
        payload += f"## Exploit scenario:\n\n"
        payload += f"{exploit_scenario}\n\n"
        
        payload += f"## Recommendation:\n\n"
        payload += f"{recommendation}\n\n" 
        
        payload += f"## Reference:\n\n"
        payload += f"{reference}\n\n"   
        payload += f"</details>\n\n"
        

    write_to_markdown(output_dir_path, payload, filename)
  

