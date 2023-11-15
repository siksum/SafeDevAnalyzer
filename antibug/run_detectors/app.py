import streamlit as st
import sys
import os
import time
from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.express as px

from antibug.utils.convert_to_json import get_root_dir

language="korean"
if language == "korean":
    language = "kr"
elif language == "english":
    language = "en"
    
filename = os.path.join(get_root_dir(), "result/detector_json_results", os.path.basename(sys.argv[1])[:-4]+f"_{language}.json")
filename_md_kr = os.path.join(get_root_dir(), "result/audit_report", os.path.basename(sys.argv[1])[:-4]+f"_kr.md")
filename_md_en = os.path.join(get_root_dir(), "result/audit_report", os.path.basename(sys.argv[1])[:-4]+f"_en.md")


# 제목
st.title('Report for Audit')


tab_titles = ['Contract Analaysis', 'Security Analysis', 'Audit Report']
tab1, tab2, tab3 = st.tabs(tab_titles)
 
# 각 탭에 콘텐츠 추가
with tab1:
    st.header('주제 A')
    # st.write('주제 A의 내용')
    data = {'Sum': [3, 5, 9, 7],
        'Confidence': ['High', 'Medium', 'Low', 'Informational']}

    df = pd.DataFrame(data)

    fig1 = px.pie(df, values='Sum', names='Confidence', title='Detected Bugs')
    st.plotly_chart(fig1)
 
with tab2:
    st.header('주제 C')
    html="""
    <button class='date-button'>2023-05-30</button>\n\n
    """
    st.markdown(html, unsafe_allow_html=True)
    
with tab3:

    st.header('Audit Report')

    # st.selectbox('Language', [])

    # 사용법
    languages = ['English', 'Korean']
    selected_lang = st.selectbox('언어를 선택해주세요', languages)

    if selected_lang == 'English':
        ret = st.write(Path(filename_md_en).read_text())
        st.markdown(ret, unsafe_allow_html=True, )
    elif selected_lang == 'Korean':
        ret=  st.write(Path(filename_md_kr).read_text())
        st.markdown(ret, unsafe_allow_html=True)
       




# # 텍스트 입력 상자
# user_input = st.text_input('이름을 입력하세요:', 'John Doe')
# st.write('안녕하세요,', user_input, '님!')

# # 숫자 입력 상자
# age = st.number_input('나이를 입력하세요:', min_value=0, max_value=150, value=30)
# st.write('당신은', age, '살 입니다.')

# # 날짜 선택
# import datetime
# today = st.date_input('오늘 날짜를 선택하세요:', datetime.date(2023, 1, 1))
# st.write('오늘은', today, '입니다.')

# # 그래프 그리기


# data = pd.DataFrame({
#     'x': np.arange(1, 11),
#     'y': np.random.randn(10)
# })

# st.line_chart(data.set_index('x'))

# # 데이터 표시
# st.write('데이터 표:', data)

# # 사진 표시
# st.image('https://www.streamlit.io/images/brand/streamlit-logo-secondary-colormark-darktext.png', width=200)

# # 인터랙티브 위젯
# if st.checkbox('데이터 분석 보기'):
#     st.write('데이터 분석 결과:')
#     st.bar_chart(data.set_index('x'))