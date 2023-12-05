import openai
import streamlit as st
import time

# OpenAI setup
assistant_id = 'asst_ZHfKM6OURUEESBMJqwhiMwRR'
openai.api_key = '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'


client = openai

# Setting up session state for chat
if "start_chat" not in st.session_state:
    st.session_state.start_chat = False
if "thread_id" not in st.session_state:
    st.session_state.thread_id = None

# Streamlit page configuration
st.set_page_config(page_title="AI-ChatBot", page_icon=":speech_balloon:")
st.title("AI ChatBot 💻")
st.write("A Simple Chat App That Answers From Your Knowledge Base.")

# Chat functionality
if st.button("Start Chat"):
    st.session_state.start_chat = True
    thread = client.beta.threads.create()
    st.session_state.thread_id = thread.id

def show_loading_icon_in_placeholder(placeholder):
    loading_html = """ 
    <div style='display: flex; justify-content: center; align-items: center;'>
        <div style='border: 5px solid #f3f3f3; border-top: 5px solid #3498db; border-radius: 50%; width: 40px; height: 40px; animation: spin 2s linear infinite;'>
        </div>
    </div>
    <style>
    @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }
    </style>
    """
    placeholder.markdown(loading_html, unsafe_allow_html=True)

if st.session_state.start_chat:
    if "messages" not in st.session_state:
        st.session_state.messages = []

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("Your question:"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)


        client.beta.threads.messages.create(
            thread_id=st.session_state.thread_id,
            role="user",
            content=prompt
        )
        loading_placeholder = st.empty()
        show_loading_icon_in_placeholder(loading_placeholder)

        run = client.beta.threads.runs.create(
            thread_id=st.session_state.thread_id,
            assistant_id=assistant_id,
            instructions="Please answer the queries using the knowledge provided in the files. When adding other information mark it clearly as such."
        )

        while run.status != 'completed':
            time.sleep(1)
            run = client.beta.threads.runs.retrieve(
                thread_id=st.session_state.thread_id,
                run_id=run.id
            )

        loading_placeholder.empty()

        messages = client.beta.threads.messages.list(
            thread_id=st.session_state.thread_id
        )

        assistant_messages_for_run = [
            message for message in messages 
            if message.run_id == run.id and message.role == "assistant"
        ]
        for message in assistant_messages_for_run:
            if message.content and hasattr(message.content[0].text, 'value'):
                response_text = message.content[0].text.value
                st.session_state.messages.append({"role": "assistant", "content": response_text})
                with st.chat_message("assistant"):
                    st.markdown(response_text)
            else:
                st.session_state.messages.append({"role": "assistant", "content": "No response text found."})
                with st.chat_message("assistant"):
                    st.markdown("No response text found.")


else:
    st.write("Click 'Start Chat' to begin the conversation.")
    