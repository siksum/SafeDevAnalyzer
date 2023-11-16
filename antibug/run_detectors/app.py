import json
import os
import streamlit as st
from streamlit_option_menu import option_menu
from streamlit_ace import st_ace
import plotly.express as px
import subprocess
import time
import openai
import toml

import pandas as pd
from antibug.utils.convert_to_json import get_root_dir
from antibug.__main__ import compile
from streamlit_chat import message

def export_to_markdown(detector_option, json_data, language):
    for detector_type, detector_data in json_data.items(): 
        detector = detector_data["results"]["detector"]
        exploit_scenario_key = f'exploit_scenario_{detector}'
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

def generate_response(prompt):
    print(openai.__version__)
    completions = openai.Completion.create (
        engine="text-davinci-003",
        prompt=prompt,
        max_tokens=1024,
        stop=None,
        temperature=0,
        top_p=1,
    )
 
    message = completions["choices"][0]["text"].replace("\n", "")
    return message

def pie_chart(level, count, color):
    if count == 0:
        return
    data = {'Vulnerability Level': [level],
            'Count': [count]}
    wine_cnt = pd.DataFrame(data)

    fig = px.pie(wine_cnt, values='Count', names='Vulnerability Level', hole=0.5, color_discrete_sequence=[color, 'red'])
    fig.add_annotation(
        text=level,
        x=0.5,  
        y=0.5,
        showarrow=False,
        font=dict(size=15),
        # color="black",
        # weight="bold"
    )
    fig.update_layout(width=300, height=300)
    st.plotly_chart(fig, use_container_width=True)

def audit_report(filename):
    st.title('Report for Audit')

    tab_titles = ['Contract Analaysis', 'Security Analysis', 'Audit Report']
    tab1, tab2, tab3 = st.tabs(tab_titles)
    detector_list=[]
    json_data= get_json_data(filename, "korean")
    confidence_count = [0, 0, 0, 0]
    for detector_type, detector_data in json_data.items(): 
        detector_list.append(detector_data["results"]["detector"])
        impact = detector_data["results"]["impact"]
        confidence = detector_data["results"]["confidence"]
        if confidence=="High":
            confidence_count[0] += 1
        elif confidence=="Medium":
            confidence_count[1] += 1
        elif confidence=="Low":
            confidence_count[2] += 1
        elif confidence=="Informational":
            confidence_count[3] += 1
            
        
    detector_list = list(set(detector_list))
    
    with tab1:
        st.header('Contract Analaysis')

    
    with tab2:
        st.header('Security Analysis')
        col1, col2, col3, col4, col5 = st.columns([2,1,1,1,1])
        with col1:
            data = {'Sum': [3, 5, 9, 7],
                'Confidence': ['High', 'Medium', 'Low', 'Informational']}

            df = pd.DataFrame(data)

            fig1 = px.pie(df, values='Sum', names='Confidence', title='Detected Bugs')
            fig1.update_layout(width=400, height=400)

            st.plotly_chart(fig1)
        with col2:
            if confidence_count[0] != 0:
                pie_chart('High', confidence_count[0], '#FF5675')
        with col3:
            if confidence_count[1] != 0:
                pie_chart('Medium', confidence_count[1], '#3CA03C')
        with col4:
            if confidence_count[2] != 0:
                pie_chart('Low', confidence_count[2], '#FFB400')
        with col5:
            if confidence_count[3] != 0:
                pie_chart('Informational', confidence_count[3], '#9986EE')
            # confidence_level =['High', 'Medium', 'Low', 'Informational']
            # for count, level in zip(confidence_count, confidence_level):
            #     if count == 0:
            #         continue
            #     data = {'Vulnerability Level': [level],
            #             'Count': [count]}
            #     wine_cnt = pd.DataFrame(data)

            #     fig = px.pie(wine_cnt, values='Count', names='Vulnerability Level', hole=0.5)
            #     fig.add_annotation(
            #         text=level,
            #         x=0.5,  
            #         y=0.5,
            #         showarrow=False,
            #         font=dict(size=20) 
            #     )
            #     fig.update_layout(width=300, height=300)
            #     st.plotly_chart(fig, use_container_width=True)

      
        


    with tab3:
        st.title('Audit Report')
        st.write('🔍 `Filename`: `{os.path.abspath(filename)}`\n')

        languages = ['English', 'Korean']
        selected_lang = st.selectbox('언어를 선택해주세요', languages)

        st.toast(f'Detect {len(detector_list)} Vulnerability! 🐞')
        time.sleep(1)
        
        options=st.multiselect('Select detector', detector_list)
        
        if selected_lang == 'English':
            for detector in options:
                json_data= get_json_data(filename, selected_lang.lower())
                export_to_markdown(detector, json_data, selected_lang.lower())
        elif selected_lang == 'Korean':
            for detector in options:
                json_data= get_json_data(filename, selected_lang.lower())
                export_to_markdown(detector, json_data, selected_lang.lower())

def main(): 
    target="shift.sol"
    st.set_page_config(page_title="Antibug", layout="wide", page_icon="🐞")
    audit_report(target)
        
        
if __name__ == "__main__":
    main()