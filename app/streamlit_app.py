import streamlit as st
from sidebar import display_sidebar
from chat_ui import display_chat_ui

st.title("Chatbot with Langchain")

# Initialize session state variables
if "messages" not in st.session_state:
    # Stores the chat history
    st.session_state.messages = []

if "session_id" not in st.session_state:
    # Keeps track of the current chat session.
    st.session_state.session_id = None

# Display the sidebar
display_sidebar()

# Display the chat ui
display_chat_ui()