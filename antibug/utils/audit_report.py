import os
import json

from typing import Optional
from datetime import datetime

from antibug.utils.convert_to_json import output_dir, get_output_path


def write_to_markdown(output_dir_path, payload, language, target: Optional[str] = None):
    if target is not None:      
        output_path= get_output_path(target, output_dir_path, language, "md")
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
        
def export_to_markdown(filename):
    output_dir_path = output_dir("audit_report")
    today_date = datetime.now().strftime("%Y-%m-%d")
    for language in ["english", "korean"]:
        if language == "korean":
            json_path = get_output_path(filename, os.path.join(os.path.dirname(output_dir_path), "detector_json_results"),"korean", "json")
            another_language_path = os.path.basename(filename)[:-4]+"_en.md"
        elif language == "english":
            json_path = get_output_path(filename, os.path.join(os.path.dirname(output_dir_path), "detector_json_results"),"english", "json")
            another_language_path = os.path.basename(filename)[:-4]+"_kr.md"
        try:
            with open(json_path, "r") as file:
                json_str = file.read()
                json_data = json.loads(json_str)
        except Exception as e:
            print(f"Failed to read {json_path}. Reason: {e}")
        
        payload = f"<button class='date-button'>{today_date}</button>\n\n"
        payload += f"# Audit Report\n\n"
        payload += f"> 🔍 `Filename`: {os.path.abspath(filename)}\n"
        payload += "---\n\n"
        if language == "english":
            payload +=f"[<button class='styled-button'>Korean</button>]({another_language_path})\n"
        elif language == "korean":
            payload +=f"[<button class='styled-button'>English</button>]({another_language_path})\n"
        payload += "<br />\n\n"
        
        payload += f"""
<style>
    .date-button{{
        color:black;
        border:none;
        font-weight: bold;
        background-color: sand;
        width: 150px;
        height: 25px;
        float: right;
        border-radius: 20px;
    }}
    .styled-button{{
        color: black;
        border: none;
        font-weight: bold;
        background-color: lightskyblue;
        width: 100px;
        height: 30px;
        float: right;
        border-radius: 20px;
    }}
    .styled-button:hover{{
        color: black;
        border: none;
        font-weight: bold;
        background-color: pink;
        width: 100px;
        height: 30px;
        float: right;
        cursor: pointer;
    }}
</style>\n\n               
"""
        for detector_type, detector_data in json_data.items(): 
            detector = detector_data["results"]["detector"]
            impact = convert_color_to_markdown(detector_data["results"]["impact"])
            confidence = convert_color_to_markdown(detector_data["results"]["confidence"])

            reference = detector_data["results"]["reference"]
            line = detector_data["results"]["element"][-1]["line"]
            code = detector_data["results"]["element"][-1]["code"]
            
            if language == "english":
                info = detector_data["results"]["info"]
                background = detector_data["results"]["background"]
                exploit_scenario = detector_data["results"]["exploit_scenario"]
                examples = detector_data["results"]["examples"]
                recommendation = detector_data["results"]["recommendation"]
                description = detector_data["results"]["description"]
            else:
                exploit_scenario = detector_data["results"]["exploit_scenario_korean"]
                recommendation = detector_data["results"]["recommendation_korean"]
                info = detector_data["results"]["info_korean"]
                description = detector_data["results"]["description_korean"]
                background = detector_data["results"]["background_korean"]
                examples = detector_data["results"]["examples_korean"]
            
            payload += f"<details>\n"
            payload += f"<summary style='font-size: 20px;'>{detector}</summary>\n"
            payload += f"<div markdown='1'>\n\n"

            payload += f"## Detect Results\n\n"
            payload += f"| Detector | Impact | Confidence | Info |\n"
            payload += f"|:---:|:---:|:---:|:---:|\n"
            payload += f"| {detector} | {impact} | {confidence} | {info} |||\n\n\n"
            payload += f"<br />\n\n"
            
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
            payload += f"<br />\n\n"
            
            
            payload += f"## Background:\n\n"
            payload += f"{background}\n\n"
            payload += f"<br />\n\n"

            payload += f"## Description:\n\n"
            payload += f"{description}\n\n"
            payload += f"<br />\n\n"
            
            payload += f"## Recommendation:\n\n"
            payload += f"{recommendation}\n\n" 
            payload += f"<br />\n\n"
            
            payload += f"## Exploit scenario:\n\n"
            payload += f"{exploit_scenario}\n\n"
            payload += f"<br />\n\n"
            
            if examples:
                payload += f"## Real World Examples:\n\n"
                payload += f"{examples}\n\n"
                payload += f"<br />\n\n"
            
            payload += f"## Reference:\n\n"
            payload += f"{reference}\n\n"   
            payload += f"</details>\n\n"
            

        write_to_markdown(output_dir_path, payload, language, filename)
  

