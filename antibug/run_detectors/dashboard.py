import json
import os
import streamlit as st
from streamlit_option_menu import option_menu
from streamlit_ace import st_ace
import plotly.express as px

import pandas as pd
from antibug.utils.convert_to_json import get_root_dir

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


def export_to_markdown(detector_option, json_data, language):
    for detector_type, detector_data in json_data.items(): 
        detector = detector_data["results"]["detector"]
        if detector_option == detector:
            impact = detector_data["results"]["impact"]
            confidence = detector_data["results"]["confidence"]
            if confidence=="High":
                confidence = 100
            elif confidence=="Medium":
                confidence = 50
            elif confidence=="Low":
                confidence = 25
            elif confidence=="Informational":
                confidence = 10

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
                
                for code in detector_data['results']['element']:
                    st.code(f"line {code['line']}: {code['code']}")
                st.markdown("---")    
                
                st.text_area("Info", value=info, height=200, max_chars=None, key=None)            
                st.markdown("---")
                
                st.subheader("Exploit scenario:")
                st.text_area("Exploit scenario", value=exploit_scenario, height=200, max_chars=None, key=None)            
                st.markdown("---")  
                
                st.subheader("Recommendation:")
                st.text_area("Recommendation", value=recommendation, height=200, max_chars=None, key=None)
                st.markdown("---")
                
                st.subheader("Reference:")
                st.text_area("Reference", value=reference, height=200, max_chars=None, key=None)
                st.markdown("---")
        else:
            continue

def get_json_data(filename, language):
    if language == "korean":
        json_path = os.path.join(get_root_dir(), "antibug/run_detectors", os.path.basename(filename)[:-4]+f"_kr.json")
    elif language == "english":
        json_path = os.path.join(get_root_dir(), "antibug/run_detectors", os.path.basename(filename)[:-4]+f"_en.json")
        
    with open(json_path, "r") as file:
        json_str = file.read()
        json_data = json.loads(json_str)
    return json_data

def audit_report(filename):
    st.title('Report for Audit')

    tab_titles = ['Contract Analaysis', 'Security Analysis', 'Audit Report']
    tab1, tab2, tab3 = st.tabs(tab_titles)
    
    with tab1:
        st.header('Contract Analaysis')
        data = {'Sum': [3, 5, 9, 7],
            'Confidence': ['High', 'Medium', 'Low', 'Informational']}

        df = pd.DataFrame(data)

        fig1 = px.pie(df, values='Sum', names='Confidence', title='Detected Bugs')
        st.plotly_chart(fig1)
    
    with tab2:
        st.header('Security Analysis')
        html="""
        <button class='date-button'>2023-05-30</button>\n\n
        """
        st.markdown(html, unsafe_allow_html=True)
        
    with tab3:
        st.title('Audit Report')
        st.write('🔍 `Filename`: `{os.path.abspath(filename)}`\n')

        languages = ['English', 'Korean']
        selected_lang = st.selectbox('언어를 선택해주세요', languages)
        detector_list=[]
        json_data= get_json_data(filename, selected_lang.lower())
        for detector_type, detector_data in json_data.items(): 
            detector_list.append(detector_data["results"]["detector"])
        detector_list = list(set(detector_list))

        options=st.multiselect('Select detector', detector_list)
        
        if selected_lang == 'English':
            for detector in options:
                json_data= get_json_data(filename, selected_lang.lower())
                export_to_markdown(detector, json_data, selected_lang.lower())
        elif selected_lang == 'Korean':
            for detector in options:
                json_data= get_json_data(filename, selected_lang.lower())
                export_to_markdown(detector, json_data, selected_lang.lower())

def sidebar():
    option = st.sidebar.selectbox(
    'Menu',
     ('페이지1', '페이지2', '페이지3'))
    
    with st.sidebar:
        choice = option_menu("Menu", ["페이지1", "페이지2", "페이지3"],
                            icons=['house', 'kanban', 'bi bi-robot'],
                            menu_icon="app-indicator", default_index=0,
                            styles={
            "container": {"padding": "4!important", "background-color": "#fafafa"},
            "icon": {"color": "black", "font-size": "25px"},
            "nav-link": {"font-size": "16px", "text-align": "left", "margin":"0px", "--hover-color": "#fafafa"},
            "nav-link-selected": {"background-color": "#08c7b4"},
        }
        )
    if choice == "페이지1":
        st.header("페이지1")
        code = st_ace(
            placeholder="Write code here...",
            language="python",
            theme="github",
            key="ace-editor"
        )
        if st.button("Run Code"):
            try:
                # Evaluate and execute the code entered in the ACE editor
                st.write(code)
            except Exception as e:
                # Handle any exceptions that occur during code execution
                st.error(f"An error occurred: {e}")

def main(): 
    target="shift.sol"
    sidebar()
    audit_report(target)
        
        
if __name__ == "__main__":
    main()