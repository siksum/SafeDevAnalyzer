import openai
import streamlit as st
import toml

secrets = toml.load("secrets.toml")
api_key = secrets["OPENAI_API_KEY"]

openai.api_key = api_key

st.title("Chat Bot (GPT-3.5)")

if "openai_model" not in st.session_state:
    st.session_state["openai_model"] = "gpt-3.5-turbo"

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("What is up?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        
        conversation = [
            {"role": m["role"], "content": m["content"]}
            for m in st.session_state.messages
        ]

        response = openai.ChatCompletion.create(
            model=st.session_state["openai_model"],
            messages=conversation,
            max_tokens=50,  
            temperature=0.7,  
            top_p=1, 
            stream=True,
        )

        for response_part in response["choices"]:
            content = response_part["message"]["content"]
            full_response += content
            message_placeholder.markdown(full_response + "▌")
            
        message_placeholder.markdown(full_response)
    
    st.session_state.messages.append({"role": "assistant", "content": full_response})
