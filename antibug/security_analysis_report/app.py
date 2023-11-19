import streamlit as st
import time
import pandas as pd
from PIL import Image
from antibug.compile.safe_dev_analyzer import SafeDevAnalyzer
from antibug.security_analysis_report.utils import get_json_data, parse_json_data_overview
from antibug.security_analysis_report.utils import parse_json_data_details



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
        
        # selected_vulnerability = st.select_slider('Confidence', options=['Informational', 'Low', 'Medium', 'High', 'All'])
        
        
        options=st.multiselect('Select detector', detector_list)
        
        if selected_lang == 'English':
            for detector in options:
                parse_json_data_details(json_file_english, selected_lang, detector)
                
        elif selected_lang == 'Korean':
            for detector in options:
                parse_json_data_details(json_file_korean, selected_lang, detector)

      
def main(): 
    st.set_page_config(page_title="Antibug", layout="wide", page_icon="🐞")

    streamlit_page()

        
        
if __name__ == "__main__":
    main()