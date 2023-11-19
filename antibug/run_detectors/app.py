import json
import os
import streamlit as st
import time
import openai
import pandas as pd
from antibug.utils.convert_to_json import get_root_dir
from PIL import Image
from antibug.compile.safe_dev_analyzer import SafeDevAnalyzer
from antibug.utils.convert_to_json import get_output_path, read_to_json

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
    html = f"""
    <div class="donut" data-percent="{level}"></div>
    """
    style = f"""
    <style>
    .donut {{
        width: calc(100% - 16px);
        padding-bottom: calc(100% - 16px);
        margin: 0 auto;
        border-radius: 50%;
        position: relative;
        text-align: center;
        transition: background .3s ease-in-out;
        background: conic-gradient({color} 0% {count}%, #F2F2F2 {count}% 100%);
    }}
    .donut::before {{
        color: #fff;
        width: 70%;
        padding: calc(35% - .64vw) 0;
        background: #264057;
        border-radius: 50%;
        position: absolute;
        left: 15%;
        top: 13%;
        display: block;
        content: attr(data-percent);
        transform: skew(-0.03deg);
        margin: auto;
        font-size: 1.1vw;
        font-size: 2vw;
        padding: calc(35% - 1.3vw) 0;
    }}
    .donut {{
        animation: pie1 0.5s forwards;
    }}
    @keyframes pie1{{
    0%{{background : conic-gradient({color} 0% 0%, #F2F2F2 0% 100%)}}
    6%{{background : conic-gradient({color} 0% 5%, #F2F2F2 0% 100%)}}
    12%{{background : conic-gradient({color} 0% 10%, #F2F2F2 0% 100%)}}
    18%{{background : conic-gradient({color} 0% 15%, #F2F2F2 0% 100%)}}
    25%{{background : conic-gradient({color} 0% 20%, #F2F2F2 0% 100%)}}
    33%{{background : conic-gradient({color} 0% 25%, #F2F2F2 0% 100%)}}
    38%{{background : conic-gradient({color} 0% 30%, #F2F2F2 0% 100%)}}
    # 44%{{background : conic-gradient({color} 0% 35%, #F2F2F2 0% 100%)}}
    100%{{background : conic-gradient({color} 0% {count}%, #F2F2F2 0% 100%)}}
    # 56%{{background : conic-gradient({color} 0% 45%, #F2F2F2 0% 100%)}}
    # 62%{{background : conic-gradient({color} 0% 50%, #F2F2F2 0% 100%)}}
    # 68%{{background : conic-gradient({color} 0% 55%, #F2F2F2 0% 100%)}}
    # 75%{{background : conic-gradient({color} 0% 60%, #F2F2F2 0% 100%)}}
    # 82%{{background : conic-gradient({color} 0% 65%, #F2F2F2 0% 100%)}}
    # 88%{{background : conic-gradient({color} 0% 70%, #F2F2F2 0% 100%)}}
    # 94%{{background : conic-gradient({color} 0% 75%, #F2F2F2 0% 100%)}}
    # 100%{{background : conic-gradient({color} 0% 80%, #F2F2F2 80% 100%)}}
    }}
    </style>
    """

    st.markdown(html, unsafe_allow_html=True)
    st.markdown(style, unsafe_allow_html=True)

def func_summary():
    instance = SafeDevAnalyzer('reentrancy.sol')
    (name, inheritance, var, func_summaries, modif_summaries) ="", "", "", "", ""
    for compilation_unit in instance.compilation_units.values():
        print(compilation_unit.contracts)
        for contract in compilation_unit.contracts:
            (name, inheritance, var, func_summaries, modif_summaries) = contract.get_summary()
    
    return (name, inheritance, var, func_summaries, modif_summaries)

def audit_report(filename):
    st.title('Report for Audit')

    tab_titles = ['Contract Analysis', 'Security Analysis', 'Audit Report']
    tab1, tab2, tab3 = st.tabs(tab_titles)
    detector_list=[]
    json_path= get_output_path(filename, "korean")
    json_data= read_to_json(json_path)
    confidence_count = [0, 0, 0, 0]
    for detector_type, detector_data in json_data.items(): 
        detector_list.append(detector_data["results"]["detector"])
        impact = detector_data["results"]["impact"]
        confidence = detector_data["results"]["confidence"]
    #     if confidence=="High":
    #         confidence_count[0] += 1
    #     elif confidence=="Medium":
    #         confidence_count[1] += 1
    #     elif confidence=="Low":
    #         confidence_count[2] += 1
    #     elif confidence=="Informational":
    #         confidence_count[3] += 1
        
    # detector_list = list(set(detector_list))
    
    with tab1:
        st.header('Contract Analysis')
        st.subheader('Call Graph')
        image = Image.open('call-graph.png')
        st.image(image, caption='Sunrise by the mountains', use_column_width=True)
        
        st.subheader('Function Summary')
        name, inheritance, var, func_summaries, modif_summaries=func_summary()
    
        data = {
            'Contract': [name],
            'Inheritance': [inheritance],
            'Variable': [var],
            'Function': [func_summaries],
            'Modifier': [modif_summaries]
        }
        function_summary = pd.DataFrame(data)
        st.dataframe(function_summary)
    with tab2:
        st.header('Security Analysis')
        
        col2, col3, col4, col5 = st.columns(4)
        # with col1:
        #     data = {'Sum': [3, 5, 9, 7],
        #         'Confidence': ['High', 'Medium', 'Low', 'Informational']}

        #     df = pd.DataFrame(data)

        #     fig1 = px.pie(df, values='Sum', names='Confidence', title='Detected Bugs')
        #     fig1.update_layout(width=400, height=400)

        #     st.plotly_chart(fig1)
        with col2:
            # if confidence_count[0] != 0:
                pie_chart('High', confidence_count[0]/sum(confidence_count)*100, '#3CA03C')       
        with col3:
            # if confidence_count[1] != 0:
                pie_chart('Medium', confidence_count[1]/sum(confidence_count)*100, '#3CA03C')
        with col4:
            # if confidence_count[2] != 0:
                pie_chart('Low', confidence_count[2]/sum(confidence_count)*100, '#3F8BC9')
        with col5:
            # if confidence_count[3] != 0:
                pie_chart('Informational', confidence_count[3]/sum(confidence_count)*100, '#9986EE')


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