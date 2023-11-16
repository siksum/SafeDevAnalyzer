import openai
import streamlit as st
import toml

# Secrets 파일로부터 API 키를 로드합니다.
secrets = toml.load("secrets.toml")
api_key = secrets["OPENAI_API_KEY"]

# OpenAI API 키를 설정합니다.
openai.api_key = api_key

# Streamlit 애플리케이션의 제목을 설정합니다.
st.title("Chat Bot (GPT-3.5)")

# 세션 상태를 초기화합니다.
if "openai_model" not in st.session_state:
    st.session_state["openai_model"] = "gpt-3.5-turbo"

if "messages" not in st.session_state:
    st.session_state.messages = []

# 이전 대화 내용을 표시합니다.
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 사용자로부터 입력을 받습니다.
if prompt := st.chat_input("What is up?"):
    # 사용자 입력을 세션 상태에 저장합니다.
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        
        # 대화 내용을 OpenAI에 보내고 응답을 받습니다.
        conversation = [
            {"role": m["role"], "content": m["content"]}
            for m in st.session_state.messages
        ]

        response = openai.ChatCompletion.create(
            model=st.session_state["openai_model"],
            messages=conversation,
            max_tokens=50,  # 최대 토큰 수 조절 (옵션)
            temperature=0.7,  # 샘플링 온도 조절 (옵션)
            top_p=1,  # 샘플링 확률 조절 (옵션)
            stream=True,
        )

        # 응답을 처리하고 표시합니다.
        for response_part in response["choices"]:
            content = response_part["message"]["content"]
            full_response += content
            message_placeholder.markdown(full_response + "▌")
            
        message_placeholder.markdown(full_response)
    
    # Assistant의 응답을 세션 상태에 저장합니다.
    st.session_state.messages.append({"role": "assistant", "content": full_response})
