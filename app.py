import streamlit as st
from chatbot import ask_gemini, ask_llama

st.set_page_config(
    page_title="Naksu AI Chatbot",
    page_icon="🤖"
)

st.title("🤖 Naksu AI Chatbot")
st.write("Chat using Gemini API or Local Llama 3")

# Model selection
model = st.selectbox(
    "Choose your model:",
    ["Gemini API", "Llama 3 (Local)"]
)

# Conversation history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display previous messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

# User input
user_input = st.chat_input("Ask me anything...")

if user_input:

    # Show user message
    with st.chat_message("user"):
        st.write(user_input)

    st.session_state.messages.append({
        "role": "user",
        "content": user_input
    })

    # Select backend
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):

            if model == "Gemini API":
                response = ask_gemini(st.session_state.messages)
            else:
                response = ask_llama(st.session_state.messages)

        st.write(response)

    st.session_state.messages.append({
        "role": "assistant",
        "content": response
    })