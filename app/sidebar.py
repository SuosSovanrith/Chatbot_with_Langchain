import streamlit as st
from api_utils import upload_document, list_documents, delete_document
import time

def get_documents():
    return list_documents()

def refresh_document_list():
    try:
        st.session_state.documents = get_documents()
    except Exception as e:
        st.sidebar.error(f"Error fetching documents: {str(e)}")


def display_sidebar():
    with st.spinner("Refreshing document..."):
        refresh_document_list()
    
    # Model selection
    model_options = ["gpt-3.5-turbo", "gpt-4o", "gpt-4o-mini"]
    st.sidebar.selectbox("Select Model", options=model_options, key="model")

    # Document upload
    uploaded_file = st.sidebar.file_uploader(
        "Choose a file", 
        type=["pdf", "docx", "html", 'htm'],
        label_visibility="collapsed"
    )
        
    if uploaded_file:
        if st.sidebar.button("Upload"):
            with st.spinner("Uploading file..."):
                try:
                    upload_response = upload_document(uploaded_file)
        
                    if upload_response:
                        st.sidebar.success(f"Uploaded with ID {upload_response['file_id']}.")
                        refresh_document_list()
                
                except Exception as e:
                    st.sidebar.error(f"Error during upload: {str(e)}")

    # List all uploaded documents
    st.sidebar.header("Uploaded Documents")

    # Display document list 
    if "documents" in st.session_state and st.session_state.documents:
        
        # list all uploaded file
        for doc in st.session_state.documents:
            st.sidebar.text(f"{doc['filename']} (ID: {doc['id']})")
        
        # refresh button
        if st.sidebar.button("Refresh"):
            refresh_document_list()
            
        # Delete functionality
        # a dictionary mapping IDs to filenames
        document_options = {doc['id']: doc['filename'] for doc in st.session_state.documents}
        
        selected_file_id = st.sidebar.selectbox(
            "Select a document to delete",
            options=list(document_options.keys()),  # IDs as options
            format_func=lambda x: document_options[x],  # Display filename for each ID
        )
            
        if st.sidebar.button("Delete"):
            if selected_file_id:
                with st.spinner("Deleting document..."):
                    try:
                        delete_response = delete_document(selected_file_id)
                            
                        if delete_response:
                            st.sidebar.success(delete_response['message'])
                            
                            with st.spinner("Refreshing document..."):
                                st.rerun()
                            
                        else:
                            st.sidebar.error("Failed to delete the document.")
                            
                    except Exception as e:
                        st.sidebar.error(f"Error during deletion: {str(e)}")
                  
            else:
                st.sidebar.info("No documents uploaded yet. Please upload a document.")
    else:
        st.sidebar.info("No documents uploaded yet. Please upload a document.")