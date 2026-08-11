import streamlit as st

from chatbot import ChatbotError, ask_gemini, ask_llama


st.set_page_config(
    page_title="Naksu AI",
    page_icon=":material/smart_toy:",
    layout="centered",
)

MODELS = {
    "Gemini API": {
        "caption": "Fast cloud responses powered by Google Gemini.",
        "status": "Online",
    },
    "Llama 3 (Local)": {
        "caption": "Runs through your connected Ollama service.",
        "status": "Local",
    },
}

SUGGESTIONS = {
    ":blue[:material/lightbulb:] Explain a concept": "Explain artificial intelligence in simple terms.",
    ":green[:material/code:] Help me code": "Help me write a Python function that reads a CSV file.",
    ":orange[:material/edit_note:] Improve my writing": "Help me improve this sentence: ",
}

if "messages" not in st.session_state:
    st.session_state.messages = []


def conversation_for_request(messages, prompt, max_messages=12):
    """Keep a valid, bounded user/assistant history for the model APIs."""
    history = [
        message
        for message in messages
        if message.get("role") in {"user", "assistant"} and message.get("content")
    ]

    # Drop a leftover user message from an earlier failed request. Failed turns
    # are not sent to the next model call, preventing consecutive user roles.
    if history and history[-1]["role"] == "user":
        history.pop()

    history = history[-max_messages:]
    if history and history[0]["role"] == "assistant":
        history = history[1:]

    return [*history, {"role": "user", "content": prompt}]

with st.sidebar:
    st.header("Naksu AI", divider="gray")
    model = st.selectbox(
        "Model",
        options=list(MODELS),
        help="Choose the model used for the next response.",
    )
    st.caption(MODELS[model]["caption"])
    st.badge(
        MODELS[model]["status"],
        icon=":material/check_circle:",
        color="green",
    )

    st.space("medium")
    if st.button(
        "Start a new chat",
        icon=":material/add_comment:",
        width="stretch",
    ):
        st.session_state.messages = []
        st.rerun()

    st.space("small")
    st.caption("Your messages stay in this browser session.")

st.title("How can I help?")
st.caption("Ask a question, brainstorm an idea, or get help with code.")

prompt = None
if not st.session_state.messages:
    with st.container(border=True):
        st.subheader("Start a conversation", anchor=False)
        st.write("Choose a suggestion or write your own message below.")
        selected_suggestion = st.pills(
            "Try one of these",
            options=list(SUGGESTIONS),
            label_visibility="collapsed",
        )
        if selected_suggestion:
            prompt = SUGGESTIONS[selected_suggestion]

for message in st.session_state.messages:
    avatar = ":material/smart_toy:" if message["role"] == "assistant" else None
    with st.chat_message(message["role"], avatar=avatar):
        st.write(message["content"])

chat_input = st.chat_input(
    "Message Naksu AI",
    submit_mode="disable",
)
if chat_input:
    prompt = chat_input

if prompt and prompt.strip():
    prompt = prompt.strip()
    request_messages = conversation_for_request(st.session_state.messages, prompt)

    with st.chat_message("user"):
        st.write(prompt)

    with st.chat_message("assistant", avatar=":material/smart_toy:"):
        with st.spinner(f"Naksu is thinking with {model}..."):
            try:
                if model == "Gemini API":
                    response = ask_gemini(request_messages)
                else:
                    response = ask_llama(request_messages)
            except ChatbotError as error:
                st.error(str(error), icon=":material/error:")
            except Exception as error:
                st.error(
                    "An unexpected error occurred. Please try again.",
                    icon=":material/error:",
                )
                with st.expander("Troubleshooting details", icon=":material/build:"):
                    st.code(type(error).__name__)
            else:
                st.write(response)
                st.session_state.messages.extend(
                    [
                        {"role": "user", "content": prompt},
                        {"role": "assistant", "content": response},
                    ]
                )
