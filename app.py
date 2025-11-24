import asyncio
import streamlit as st

from main import initialize_backend, process_message


st.set_page_config(page_title="Fraud Detection Agent", layout="wide")
st.title("Fraud Detection Agent")

@st.cache_resource
def init_backend():
    """Initialize backend and cache it for the entire session"""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    db, graph = loop.run_until_complete(initialize_backend())
    return db, graph, loop


db, graph, loop = init_backend()

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

if prompt := st.chat_input("Enter your question:", key="chat_input"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Processing..."):
            try:
                response = loop.run_until_complete(process_message(graph, prompt))
                st.write(response)
                st.session_state.messages.append({"role": "assistant", "content": response})
            except Exception as e:
                st.error(f"Error: {str(e)}")