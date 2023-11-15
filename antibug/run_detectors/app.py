import streamlit as st

# 제목
st.title('나의 첫 Streamlit 대시보드')

# 텍스트 입력 상자
user_input = st.text_input('이름을 입력하세요:', 'John Doe')
st.write('안녕하세요,', user_input, '님!')

# 숫자 입력 상자
age = st.number_input('나이를 입력하세요:', min_value=0, max_value=150, value=30)
st.write('당신은', age, '살 입니다.')

# 날짜 선택
import datetime
today = st.date_input('오늘 날짜를 선택하세요:', datetime.date(2023, 1, 1))
st.write('오늘은', today, '입니다.')

# 그래프 그리기
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

data = pd.DataFrame({
    'x': np.arange(1, 11),
    'y': np.random.randn(10)
})

st.line_chart(data.set_index('x'))

# 데이터 표시
st.write('데이터 표:', data)

# 사진 표시
st.image('https://www.streamlit.io/images/brand/streamlit-logo-secondary-colormark-darktext.png', width=200)

# 인터랙티브 위젯
if st.checkbox('데이터 분석 보기'):
    st.write('데이터 분석 결과:')
    st.bar_chart(data.set_index('x'))