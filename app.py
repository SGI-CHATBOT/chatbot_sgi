import streamlit as st
from google import genai

st.title("😊 재무제표 입수 프로세스 챗봇")

GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
client = genai.Client(api_key=GEMINI_API_KEY)

try:
    with open("knowledge_v1.txt", "r", encoding="utf-8") as f:
        custom_knowledge = f.read()
except FileNotFoundError:
    custom_knowledge = "별도의 전용 학습 데이터가 없습니다."

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("예시 : 외감기업인데, 재무제표 입수 언제될까?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        
        system_instruction = f"""너는 사용자가 제공한 참고자료만을 바탕으로 답변하는 챗봇이야. 자료에 없는 내용은 모른다고 답변해줘.
        [답변 시 참고사항]은 너만 알면 되는 부분이니까 안내에는 사용하지마.\n\n[참고자료]\n{custom_knowledge}"""
        
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
        unanswered_keywords = ["학습하지 못한", "참고자료에 없는", "모른다고"]
        
        if any(keyword in full_response for keyword in unanswered_keywords):
            # Specify the file path to record (same location as knowledge.txt)
            log_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "unanswered.txt")
            
            # Formatting the current time and the user's question
            current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            log_entry = f"[{current_time}] 질문: {prompt}\n"
            
            # Append to file
            with open(log_path, "a", encoding="utf-8") as f:
                f.write(log_entry)
                
    st.session_state.messages.append({"role": "assistant", "content": full_response})
