from fastapi import FastAPI, File, UploadFile, HTTPException
from pydantic_models import QueryInput, QueryResponse, DocumentInfo, DeleteFileRequest
from langchain_utils import get_rag_chain
from db_utils import insert_application_logs, get_chat_history, get_all_documents, insert_document_record, delete_document_record
from chroma_utils import index_document_to_chroma, delete_doc_from_chroma
import os
import uuid
import logging
import shutil
import os

    
# Setting up for logging our app's info
logging.basicConfig(filename='app.log', level=logging.INFO)

# Initialize FastAPI 
fapi = FastAPI()


# api endpoint for chatting
@fapi.post("/chat", response_model=QueryResponse)
def chat(query_input: QueryInput):
    # Create a new session_id with uuid if it is not provided 
    session_id = query_input.session_id or str(uuid.uuid4())
    logging.info(f"Session ID: {session_id}, User Query: {query_input.question}, Model: {query_input.model.value}")

    # Get all chats history from our database
    chat_history = get_chat_history(session_id)
    
    # Invokes the RAG chain to generate a response
    rag_chain = get_rag_chain(query_input.model.value)
    answer = rag_chain.invoke({
        "input": query_input.question,
        "chat_history": chat_history
    })['answer']

    # Store logs of this chat in our database
    insert_application_logs(session_id, query_input.question, answer, query_input.model.value)
    logging.info(f"Session ID: {session_id}, AI Response: {answer}")
    return QueryResponse(answer=answer, session_id=session_id, model=query_input.model)


# Api endpoint for uploading document
@fapi.post("/upload")
def upload_document(file: UploadFile = File(...)):
    allowed_extensions = ['.pdf', '.docx', '.html', '.htm']
    file_extension = os.path.splitext(file.filename)[1].lower()

    if file_extension not in allowed_extensions:
        raise HTTPException(status_code=400, detail=f"Unsupported file type. Allowed types are: {', '.join(allowed_extensions)}")

    # Save the uploaded file to a temporary file
    temp_file_path = f"temp_{file.filename}"
    
    try:
        with open(temp_file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Insert file record into database
        file_id = insert_document_record(file.filename)
        
        # Index the documents in Chroma 
        success = index_document_to_chroma(temp_file_path, file_id)

        if success:
            return {"message": f"File {file.filename} has been successfully uploaded and indexed.", "file_id": file_id}
        else:
            delete_document_record(file_id)
            raise HTTPException(status_code=500, detail=f"Failed to index {file.filename}.")
        
    finally:
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)
         
            
# Api endpoint for listing all documents that have been uploaded
@fapi.get("/list", response_model=list[DocumentInfo])
def list_documents():
    return get_all_documents()


# Api endpoint for deleting document
@fapi.post("/delete")
def delete_document(request: DeleteFileRequest):
    # Delete document from Chroma first
    chroma_delete_success = delete_doc_from_chroma(request.file_id)

    # Once success, delete the document from our database
    if chroma_delete_success:
        db_delete_success = delete_document_record(request.file_id)
        
        if db_delete_success:
            return {"message": f"Successfully deleted document with file_id {request.file_id}."}
        else:
            return {"error": f"Failed to delete document with file_id {request.file_id} from the database."}
    else:
        return {"error": f"Failed to delete document with file_id {request.file_id} from Chroma."}