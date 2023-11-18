import json
import glob
import os
import streamlit as st
import time
import pandas as pd
from antibug.utils.convert_to_json import get_root_dir
from PIL import Image
from antibug.compile.safe_dev_analyzer import SafeDevAnalyzer
from antibug.utils.convert_to_json import get_output_path, read_to_json, output_dir

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
    print(json_data)
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


def write_audit_report(detector, impact, confidence, reference, code, description, exploit_scenario, recommendation, info):
    st.expander("detector")
            
    with st.expander(detector):
        st.header(detector)
        st.subheader("Detect Results")
        df = pd.DataFrame({
            'Detector': [detector],
            'Impact': [impact],
            'Confidence': [confidence],
            'Info': [description]
        })
        
        column_config = {
            'Detector': {'editable': False},
            'Confidence': st.column_config.ProgressColumn(
                "Confidence",
                min_value=0,
                max_value=100,
                # format=f"{detector}%",
            ),
            'Impact': {'editable': False},
            'Info': {'editable': False}
        }

        st.data_editor(df, column_config=column_config)
        st.markdown("---")                

        st.subheader("Vulnerabiltiy in code:")
        for line_and_code in code:
            st.code(f"line {line_and_code['line']}: {line_and_code['code']}")
        st.write(info)
        # st.text_area("Info", value=info, height=200, max_chars=None, key=None)            
        st.markdown("---")
        
        st.subheader("Exploit scenario:")
        code_start = exploit_scenario.find("```solidity")
        if code_start != -1:
            code_start += len("```solidity")
            code_end = exploit_scenario.find("```", code_start)
            if code_end != -1:
                exploit_scenario_code = exploit_scenario[code_start:code_end].strip()
        exploit_scenario_description = exploit_scenario[code_end + 3:].strip()

        st.code(exploit_scenario_code)
        st.write(exploit_scenario_description)
        # st.text_area("Exploit scenario", value=exploit_scenario_description, height=200, max_chars=None, key=exploit_scenario_key)            
        st.markdown("---")  
        
        st.subheader("Recommendation:")
        st.write(recommendation)
        # st.text_area("Recommendation", value=recommendation, height=200, max_chars=None, key=None)
        st.markdown("---")
        
        st.subheader("Reference:")
        st.write(reference)
        # st.text_area("Reference", value=reference, height=200, max_chars=None, key=None)
        st.markdown("---")


def streamlit_page():
    st.title('Report for Audit')

    tab_titles = ['Contract Analysis', 'Security Analysis', 'Audit Report']
    contract_analysis_tab, security_analysis_tab, audit_report_tab = st.tabs(tab_titles)
    json_file_english, json_file_korean = get_json_data()
    filename, detector_list, confidence_count, impact_count = parse_json_data_overview(json_file_english)
    
    
    with contract_analysis_tab:
        st.header('Contract Analysis')
        st.subheader('Call Graph')
    
    with security_analysis_tab:
        st.header('Security Analysis')
    
    with audit_report_tab:
        st.header('Audit Report')
        st.write(f'🔍 `Filename`: `{filename}`\n')
        
        st.toast(f'Detect {len(detector_list)} Vulnerability! 🐞')
        time.sleep(1)
        
        languages = ['English', 'Korean']
        selected_lang = st.selectbox('언어를 선택해주세요', languages)
        
        options=st.multiselect('Select detector', detector_list)
        
        if selected_lang == 'English':
            for detector in options:
                parse_json_data_details(json_file_english, selected_lang, detector)
                
        elif selected_lang == 'Korean':
            for detector in options:
                parse_json_data_details(json_file_korean, selected_lang, detector)

      
  


    

def main(): 
    st.set_page_config(page_title="Antibug", layout="wide", page_icon="🐞")
    # audit_report(filename)

    streamlit_page()

        
        
if __name__ == "__main__":
    main()