import os
import glob
import json
from antibug.utils.convert_to_json import get_root_dir
from antibug.security_analysis_report.write_page import write_audit_report



def get_json_path_list():
    json_files = []
    output_dir = os.path.join(get_root_dir(), f"result/detector_json_results")
    json_files = glob.glob(os.path.join(output_dir, '*.json'))
    return json_files

def get_json_data():
    json_files=get_json_path_list()
    json_data = {}
    language_list = ["English", "Korean"]
    for json_file, language in zip(json_files, language_list):
        with open(json_file, "r") as file:
            json_str = file.read()
            json_data[language] =json.loads(json_str)
    
    return json_data["English"], json_data["Korean"]


def parse_json_data_overview(json_data):
    detector_list=[]
    confidence_count = [0, 0, 0, 0]
    impact_count = [0, 0, 0, 0]
    for detector_type, detector_data in json_data.items():
        filename=detector_data["results"]["filename"] 
        detector_list.append(detector_data["results"]["detector"])
        impact = detector_data["results"]["impact"]
        confidence = detector_data["results"]["confidence"]
        if confidence=="High":
            confidence_count[0] += 1
            impact_count[0] += 1
        elif confidence=="Medium":
            confidence_count[1] += 1
            impact_count[1] += 1
        elif confidence=="Low":
            confidence_count[2] += 1
            impact_count[2] += 1
        elif confidence=="Informational":
            confidence_count[3] += 1
            impact_count[3] += 1
        
    detector_list = list(set(detector_list))
    return filename, detector_list, confidence_count, impact_count


def parse_json_data_details(json_data, language, detector_option):
    for detector_type, detector_data in json_data.items():
        detector = detector_data["results"]["detector"]

        if detector_option == detector:
            impact = detector_data["results"]["impact"]
            confidence = detector_data["results"]["confidence"]
            reference = detector_data["results"]["reference"]
            code = detector_data["results"]["element"]
            
            if language == "English":
                description = detector_data["results"]["info"]
                exploit_scenario = detector_data["results"]["exploit_scenario"]
                recommendation = detector_data["results"]["recommendation"]
                info = detector_data["results"]["description"]
            else:
                exploit_scenario = detector_data["results"]["exploit_scenario_korean"]
                recommendation = detector_data["results"]["recommendation_korean"]
                description = detector_data["results"]["info_korean"]
                info = detector_data["results"]["description_korean"]
            write_audit_report(detector, impact, confidence, reference, code, description, exploit_scenario, recommendation, info)
        else:
            continue
