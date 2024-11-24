import streamlit as st
from api_utils import upload_document, list_documents, delete_document

def display_sidebar():
    # Model selection
    model_options = ["gpt-4o", "gpt-4o-mini"]
    st.sidebar.selectbox("Select Model", options=model_options, key="model")

    # Document upload
    uploaded_file = st.sidebar.file_uploader("Choose a file", type=["pdf", "docx", "html", 'htm'])
    if uploaded_file and st.sidebar.button("Upload"):
        with st.spinner("Uploading..."):
            upload_response = upload_document(uploaded_file)
            if upload_response:
                st.sidebar.success(f"File uploaded successfully with ID {upload_response['file_id']}.")
                # Store all uploaded documents in a session state 
                st.session_state.documents = list_documents()

    # List all uploaded documents
    st.sidebar.header("Uploaded Documents")
    if st.sidebar.button("Refresh Document List"):
        st.session_state.documents = list_documents()

    # Display document list 
    if "documents" in st.session_state and st.session_state.documents:
        for doc in st.session_state.documents:
            st.sidebar.text(f"{doc['filename']} (ID: {doc['id']})")

        # Delete functionality
        selected_file_id = st.sidebar.selectbox("Select a document to delete", options=[doc['id'] for doc in st.session_state.documents])
        
        if st.sidebar.button("Delete"):
            delete_response = delete_document(selected_file_id)
            if delete_response:
                st.sidebar.success(f"Document deleted successfully.")
                st.session_state.documents = list_documents()