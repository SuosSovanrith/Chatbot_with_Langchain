from langchain_community.document_loaders import PyPDFLoader, Docx2txtLoader, UnstructuredHTMLLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma
from typing import List
from langchain_core.documents import Document
from dotenv import load_dotenv
import os
import logging
from datetime import datetime

# set api key enviroment
def load_openai_api_key():
    load_dotenv()
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY is missing from environment variables")
    return api_key

# Initialize the OpenAI API key once to avoid multiple calls
api_key = load_openai_api_key()
os.environ["OPENAI_API_KEY"] = api_key

# Setting up for logging our app's info
logging.basicConfig(filename='app.log', level=logging.INFO)

# Get log time
def log_time():
    return datetime.now().strftime("%d:%m:%Y %H:%M:%S")


# Initialize text splitter to split documents into manageable chunks 
text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200, length_function=len)

# Embedding function for document
embedding_function = OpenAIEmbeddings()

# Initialize Chroma vector store
vectorstore = Chroma(persist_directory="./chroma_db", embedding_function=embedding_function)

# Supported file extensions
SUPPORTED_EXTENSIONS = {
    '.pdf': PyPDFLoader,
    '.docx': Docx2txtLoader,
    '.html': UnstructuredHTMLLoader,
    '.htm': UnstructuredHTMLLoader
}

# Handles loading different document types and splitting them into chunks.
def load_and_split_document(file_path: str) -> List[Document]:
    file_extension = os.path.splitext(file_path)[-1].lower()
    loader_class = SUPPORTED_EXTENSIONS.get(file_extension)
    
    if loader_class is None:
        raise ValueError(f"Unsupported file type: {file_extension}")
    
    # bad code
    # if file_path.endswith('.pdf'):
    #     loader = PyPDFLoader(file_path)
    # elif file_path.endswith('.docx'):
    #     loader = Docx2txtLoader(file_path)
    # elif file_path.endswith('.html') or file_path.endswith('.htm'):
    #     loader = UnstructuredHTMLLoader(file_path)
    # else:
    #     raise ValueError(f"Unsupported file type: {file_path}")
    
    loader = loader_class(file_path)
    
    documents = loader.load()
    return text_splitter.split_documents(documents)

#  Takes a file path and a file ID to loads and splits the document, then adds metadata of file_id to each split to link vector store entries back to our database records, then adds these document chunks to our Chroma vector store.
def index_document_to_chroma(file_path: str, file_id: int) -> bool:
    try:
        splits = load_and_split_document(file_path)

        # Add metadata of file_id to each split
        for split in splits:
            split.metadata['file_id'] = file_id

        # adds these document chunks to our Chroma vector store.
        logging.info(f"Successfully indexed {len(splits)} document chunks from {file_path} with file_id {file_id} [{log_time()}]")
        vectorstore.add_documents(splits)
        return True
    
    except Exception as e:
        # print(f"Error indexing document: {e}")
        logging.error(f"Error indexing document {file_path} with file_id {file_id}: {str(e)} [{log_time()}]")
        return False
    

# Deletes all document chunks by file_id from the Chroma vector store
def delete_doc_from_chroma(file_id: int):
    try:
        docs = vectorstore.get(where={"file_id": file_id})
        # print(f"Found {len(docs['ids'])} document chunks for file_id {file_id}")
        logging.info(f"Found {len(docs['ids'])} document chunks for file_id {file_id} [{log_time()}]")

        vectorstore._collection.delete(where={"file_id": file_id})
        print(f"Deleted all documents with file_id {file_id}")
        logging.info(f"Deleted all documents with file_id {file_id} [{log_time()}]")

        return True
    
    except Exception as e:
        # print(f"Error deleting document with file_id {file_id} from Chroma: {str(e)}")
        logging.error(f"Error deleting document chunks with file_id {file_id} from Chroma: {str(e)} [{log_time()}]")
        return False