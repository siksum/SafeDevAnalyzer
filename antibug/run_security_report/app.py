import streamlit as st
import time
from antibug.run_security_report.utils import get_json_data, parse_json_data_overview
from antibug.run_security_report.utils import parse_json_data_details, call_graph_path, parse_contract_analysis_data, read_contract_analysis_json


def streamlit_page():
    st.title('Audit Report')
    
    # tab_titles = ['Contract Analysis', 'Security Analysis', 'Audit Report']
    # contract_analysis_tab, security_analysis_tab, audit_report_tab = st.tabs(tab_titles)
    json_file_english, json_file_korean = get_json_data()
    filename, detector_list, confidence_count, impact_count = parse_json_data_overview(json_file_english)
    
    
    # with contract_analysis_tab:
    #     st.header('Contract Analysis')
    #     st.subheader('Call Graph')
    #     st.expander('Show Call Graph')
    #     with st.expander('Show Call Graph'):
    #         st.subheader('Call Graph')
    #         st.image(call_graph_path())
    #     contract_list = []
    #     json_data = read_contract_analysis_json()
    #     for contract_name, contract_data in json_data.items():
    #         contract_list.append(contract_name)
        
    #     st.markdown("---")
        
    #     st.subheader('Contract Analysis')
    #     options=st.multiselect('', contract_list)
    #     if options:
    #         for contract_name in options:
    #             parse_contract_analysis_data(contract_name, json_data)
        

    # with security_analysis_tab:
    #     st.header('Security Analysis')
        
    
    # with audit_report_tab:
    # st.header('Audit Report')
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
    streamlit_page()

        
if __name__ == "__main__":
    main()
