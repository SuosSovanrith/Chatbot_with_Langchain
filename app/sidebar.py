import streamlit as st
from api_utils import upload_document, list_documents, delete_document
import time

@st.cache_data
def get_documents_cached():
    return list_documents()


def display_sidebar():
        
    # Model selection
    # model_options = ["gpt-4o", "gpt-4o-mini", "gpt-3.5-turbo"]
    model_options = ["gpt-3.5-turbo"] # limit to only this model because of free tier
    st.sidebar.selectbox("Select Model", options=model_options, key="model")

    # Document upload
    uploaded_file = st.sidebar.file_uploader(
        "Choose a file", 
        type=["pdf", "docx", "html", 'htm'],
        label_visibility="collapsed"
    )
        
    if uploaded_file and st.sidebar.button("Upload"):
        try:
            upload_response = upload_document(uploaded_file)
      
            if upload_response:
                st.sidebar.success(f"File uploaded successfully with ID {upload_response['file_id']}.")
                # Store all uploaded documents in a session state 
                st.session_state.documents = get_documents_cached()
        
        except Exception as e:
            st.sidebar.error(f"Error during upload: {str(e)}")

    # List all uploaded documents
    st.sidebar.header("Uploaded Documents")
    if st.sidebar.button("Refresh Document List"):
        try:
            st.session_state.documents = get_documents_cached()
        except Exception as e:
            st.sidebar.error(f"Error fetching documents: {str(e)}")

    # Display document list 
    if "documents" in st.session_state and st.session_state.documents:
        for doc in st.session_state.documents:
            st.sidebar.text(f"{doc['filename']} (ID: {doc['id']})")

        # Delete functionality
        selected_file_id = st.sidebar.selectbox(
            "Select a document to delete", 
            options=[doc['id'] for doc in st.session_state.documents],
            index=0 if st.session_state.documents else None
        )
        
        if st.sidebar.button("Delete"):
            if selected_file_id:
                try:
                    delete_response = delete_document(selected_file_id)
                        
                    if delete_response:
                        st.sidebar.success(f"Document deleted successfully.")
                        st.session_state.documents = get_documents_cached()
                    else:
                        st.sidebar.error("Failed to delete the document.")
                        
                except Exception as e:
                    st.sidebar.error(f"Error during deletion: {str(e)}")
            else:
                st.sidebar.info("No documents uploaded yet. Please upload a document.")