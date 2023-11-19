import streamlit as st
import pandas as pd

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
        st.markdown("---")  
        
        st.subheader("Recommendation:")
        st.write(recommendation)
        st.markdown("---")
        
        st.subheader("Reference:")
        st.write(reference)
        st.markdown("---")
        
def write_contract_analysis_report(contract_name, inheritance, state_variable_list, function_list):
    
    with st.expander(contract_name):
        st.subheader("Inheritance")
        if inheritance == []:
            inheritance == "None"
        st.write(inheritance)
        st.markdown("---")
            
        st.subheader("State Variables")
        if state_variable_list== []:
            st.write("None")
        else:
            for state_variable in state_variable_list.values():
                if state_variable["Signature"] == []:
                    state_variable["Signature"] == "None"
                if state_variable["Slot"] == []:
                    state_variable["Slot"] == "None"
                if state_variable["Offset"] == []:
                    state_variable["Offset"] == "None"
                
                df = pd.DataFrame({
                    'State Variable': [state_variable["Name"]],
                    'Signature': [state_variable["Signature"]],
                    'Slot': [state_variable["Slot"]],
                    'Offset': [state_variable["Offset"]],
                })
                unique_key = f'{contract_name}_{state_variable["Name"]}'
                st.data_editor(df, key=unique_key, column_config={'State Variable': {'editable': False}})
            
            st.markdown("---")
        
        st.subheader("Function Summaries")
        if function_list == []:
            st.write("None")
        else:
            for function in function_list.values():
                if function["Signature"] == []:
                    function["Signature"] == "None"
                if function["Visibility"] == []:
                    function["Visibility"] == "None"
                if function["Modifiers"] == []:
                    function["Modifiers"] == "None"
                if function["Internal Calls"] == []:
                    function["Internal Calls"] == "None"
                if function["External Calls"] == []:
                    function["External Calls"] == "None"
                df = pd.DataFrame({
                    'Function Name': [function["Name"]],
                    'Signature': [function["Signature"]],
                    'Visibility': [function["Visibility"]],
                    'Modifiers': [function["Modifiers"]],
                    'Internal Calls': [function["Internal Calls"]],
                    'External Calls': [function["External Calls"]],
                })
                
    
                st.data_editor(df, column_config={'Function Name': {'editable': False}})
            st.markdown("---")
    
    