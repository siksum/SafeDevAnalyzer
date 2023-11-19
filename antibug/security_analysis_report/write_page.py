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