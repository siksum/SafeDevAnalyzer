import json
import os
import streamlit as st
from streamlit_option_menu import option_menu
from streamlit_ace import st_ace
import plotly.express as px
import subprocess

import pandas as pd
from antibug.utils.convert_to_json import get_root_dir
from antibug.__main__ import compile

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
    
    with tab3:
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
        
    with tab1:
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
        st.write('Selected detectors:', options)
        
        if selected_lang == 'English':
            for detector in options:
                json_data= get_json_data(filename, selected_lang.lower())
                export_to_markdown(detector, json_data, selected_lang.lower())
        elif selected_lang == 'Korean':
            for detector in options:
                json_data= get_json_data(filename, selected_lang.lower())
                export_to_markdown(detector, json_data, selected_lang.lower())

def sidebar(target):
    st.sidebar.title("Antibug")
    
    with st.sidebar:
        choice = option_menu("Menu", ["Compile & Deploy", "Security Check", "Run Testcode"],
                            icons=['house', 'kanban', 'bi bi-robot'],
                            menu_icon="app-indicator", default_index=0,
                            styles={
            "container": {"padding": "4!important", "background-color": "#fafafa"},
            "icon": {"color": "black", "font-size": "25px"},
            "nav-link": {"font-size": "16px", "text-align": "left", "margin":"0px", "--hover-color": "#fafafa"},
            "nav-link-selected": {"background-color": "#08c7b4"},
        }
        )
    
    if choice == "Compile & Deploy":
        filename =""
        st.sidebar.header("Compile & Deploy")
        st.sidebar.subheader("Compile")
        uploaded_file=st.sidebar.file_uploader("Upload Solidity File", type="sol")
        
        if uploaded_file is not None:
            filename=uploaded_file.name
        button=st.sidebar.markdown("""
            <style>
            .compile-button {
            background-color: skyblue;
            color: white;
            padding: 14px 20px;
            margin: 8px 0;
            border: none;
            cursor: pointer;
            width: 100%;
            }
            .compile-button:hover {
            opacity: 0.8;
            }
            </style>
            <button class="compile-button">Compile</button>
            """, unsafe_allow_html=True)
        
        
        st.sidebar.subheader("Interaction")
        st.sidebar.selectbox("Chian", ["MainNet"])
        st.sidebar.selectbox("From Address", ["0xf76ecb39df4a43321721a0add89af2ff57b018f9"])
        st.sidebar.number_input('Gas Limit', min_value=0, max_value=9000000)
        st.sidebar.number_input('Value', min_value=0, max_value=9000000)
        
        st.sidebar.subheader("Deploy")
        st.sidebar.selectbox("Contract", ["EtherStore"])
        
        button=st.sidebar.markdown("""
            <style>
            .deploy-button {
            background-color: skyblue;
            color: white;
            padding: 14px 20px;
            margin: 8px 0;
            border: none;
            cursor: pointer;
            width: 100%;
            }
            .deploy-button:hover {
            opacity: 0.8;
            }
            </style>
            <button class="deploy-button">Deploy</button>
            """, unsafe_allow_html=True)
    
    elif choice == "Security Check":
        st.sidebar.header("Security Check")
        st.sidebar.subheader("Select Detector")
        st.sidebar.selectbox("Detector", ["Reentrancy", "Integer Overflow/Underflow", "Unprotected Ether Withdrawal", "Unchecked Call Return Value", "Unprotected"])
        
       
        if st.sidebar.button("Analysis", key="analysis"):
            audit_report(target)
        else: 
            st.title("Vulnerability Detection List")
            
        button = """
         <style>
        [data-testid="baseButton-secondary"] {
            background-color: skyblue;
            color: white;
            padding: 14px 20px;
            margin: 8px 0;
            border: none;
            cursor: pointer;
            width: 100%; 
        }
        [data-testid="baseButton-secondary"]:active {
            background-color: pink;
            color: white;
            padding: 14px 20px;
            margin: 8px 0;
            border: none;
            cursor: pointer;
            width: 100%; 
        }
        </style>
        """
            
        st.sidebar.markdown(button, unsafe_allow_html=True)

    elif choice == "Run Testcode":
        st.header("Run Testcode")
        st.subheader("Select Testcode")
        language=st.selectbox("Testcode", ["python", "javascript", "javascript_test"])
        
        code = st_ace(
            placeholder="Write code here...",
            language="python",
            theme="github",
            key="ace-editor",
            show_gutter=False,
        )
        result =code
        if st.button("Run Code"):
            if language == "python":
                with open ("shift.py", "w") as f:
                    f.write(result)
                
                process = subprocess.Popen(
                ['python3', 'shift.py'],  
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE, 
                )
                stdout, stderr = process.stdout.read().decode('utf-8'), process.stderr.read().decode('utf-8')

                st.subheader("Output:")
                st.code(stdout, language="python")

                if stderr:
                    st.subheader("Error:")
                    st.code(stderr, language="python")
            elif language == "javascript":
                with open ("shift.js", "w") as f:
                    f.write(result)
                
                process = subprocess.Popen(
                ['node', 'shift.js'],  
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE, 
                )
                stdout, stderr = process.stdout.read().decode('utf-8'), process.stderr.read().decode('utf-8')

                st.subheader("Output:")
                st.code(stdout, language="javascript")

                if stderr:
                    st.subheader("Error:")
                    st.code(stderr, language="javascript")
            elif language == "javascript_test":
                with open ("shift.test.js", "w") as f:
                    f.write(result)
                
                process = subprocess.Popen(
                ['npm', 'test'],  
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE, 
                text=True
                )
                st.subheader("Output:")
                # st.code(iter(process.stdout.readline, b''), language="javascript")
                
                result =""
                for line in iter(process.stdout.readline, b''):
                    st.write(result)
                #     st.code(line, language="javascript")
                
                
                # stdout, stderr = process.stdout.read().decode('utf-8'), process.stderr.read().decode('utf-8')

                
                if process.stderr:
                    st.subheader("Error:")
                    for line in iter(process.stderr.readline, b''):
                        st.code(line, language="javascript")
                # return_code = process.returncode
    
def main(): 
    target="shift.sol"
    st.set_page_config(page_title="Antibug", layout="wide", page_icon="🐞")
    
    sidebar(target)
        
        
if __name__ == "__main__":
    main()