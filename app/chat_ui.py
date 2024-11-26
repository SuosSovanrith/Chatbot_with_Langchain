import streamlit as st
from api_utils import get_api_response

def display_chat_ui():
    # Initialize session state if it doesn't exist
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "session_id" not in st.session_state:
        st.session_state.session_id = None
    if "model" not in st.session_state:
        st.session_state.model = "gpt-3.5-turbo"  # Default model, could be adjustable in the UI
        
    # Display chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            if message["role"] == "user":
                st.markdown(f">>You: {message['content']}")
            else:
                st.markdown(f">>Chatbot: {message['content']}")

    # Add some space to separate the chat history from new input
    st.markdown("<hr>", unsafe_allow_html=True)
    
    # Handle new user input 
    if prompt := st.chat_input("Message chatbot..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(f">>You: {prompt}")

        # Get API response
        with st.spinner("Generating response..."):
            try:
                response = get_api_response(prompt, st.session_state.session_id, st.session_state.model)

                if response:
                    st.session_state.session_id = response.get('session_id')
                    st.session_state.messages.append({"role": "assistant", "content": response['answer']})

                    with st.chat_message("assistant"):
                        st.markdown(f">>Chatbot: {response['answer']}")

                    with st.expander("Details"):
                        st.subheader("Generated Answer")
                        st.code(response['answer'])
                        st.subheader("Model Used")
                        st.code(response['model'])
                        st.subheader("Session ID")
                        st.code(response['session_id'])
                else:
                    st.error("Failed to get a response from the API. Please try again.")
            
            except Exception as e:
                st.error(f"An error occurred: {e}")
                
    # A button to clear the chat history if there are any
    if st.session_state.messages != []:
        if st.button("Clear Chat"):
            st.session_state.messages = []