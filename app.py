import streamlit as st
from google import genai

st.title("💬 제미나이 코랩 챗봇")

GEMINI_API_KEY = "AIzaSyBh0CJKoMlkWRcQWLuFsSQsm6sd33Gwjc8"
client = genai.Client(api_key=GEMINI_API_KEY)

try:
    with open("knowledge.txt", "r", encoding="utf-8") as f:
        custom_knowledge = f.read()
except FileNotFoundError:
    custom_knowledge = "별도의 전용 학습 데이터가 없습니다."

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("제미나이에게 무엇이든 물어보세요!"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        
        system_instruction = f"너는 사용자가 제공한 참고자료만을 바탕으로 답변하는 챗봇이야. 자료에 없는 내용은 모른다고 답변해줘.\n\n[참고자료]\n{custom_knowledge}"
        
        # 🔥 에러 해결의 핵심 부분!
        formatted_messages = []
        for m in st.session_state.messages:
            # 사용자는 USER로, AI 응답은 MODEL로 변경합니다.
            role = "USER" if m["role"] == "user" else "MODEL"
            formatted_messages.append({"role": role, "parts": [{"text": m["content"]}]})
            
        response = client.models.generate_content_stream(
            model='gemini-2.5-flash',
            contents=formatted_messages,
            config=dict(system_instruction=system_instruction)
        )
        
        for chunk in response:
            if chunk.text:
                full_response += chunk.text
                message_placeholder.markdown(full_response + "▌")
        message_placeholder.markdown(full_response)
        
    st.session_state.messages.append({"role": "assistant", "content": full_response})
