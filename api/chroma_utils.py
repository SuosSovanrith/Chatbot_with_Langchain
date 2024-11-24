from langchain_community.document_loaders import PyPDFLoader, Docx2txtLoader, UnstructuredHTMLLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma
from typing import List
from langchain_core.documents import Document
from dotenv import load_dotenv
import os

# set api key enviroment
load_dotenv()
if not os.environ.get("OPENAI_API_KEY"):
    os.environ["OPENAI_API_KEY"] = os.getenv('OPENAI_API_KEY')
    
# Initialize text splitter to split documents into manageable chunks 
text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200, length_function=len)

# Embedding function for document
embedding_function = OpenAIEmbeddings()

# Initialize Chroma vector store
vectorstore = Chroma(persist_directory="./chroma_db", embedding_function=embedding_function)

# Handles loading different document types and splitting them into chunks.
def load_and_split_document(file_path: str) -> List[Document]:
    if file_path.endswith('.pdf'):
        loader = PyPDFLoader(file_path)
    elif file_path.endswith('.docx'):
        loader = Docx2txtLoader(file_path)
    elif file_path.endswith('.html') or file_path.endswith('.htm'):
        loader = UnstructuredHTMLLoader(file_path)
    else:
        raise ValueError(f"Unsupported file type: {file_path}")

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
        vectorstore.add_documents(splits)
        return True
    
    except Exception as e:
        print(f"Error indexing document: {e}")
        return False
    

# Deletes all document chunks by file_id from the Chroma vector store
def delete_doc_from_chroma(file_id: int):
    try:
        docs = vectorstore.get(where={"file_id": file_id})
        print(f"Found {len(docs['ids'])} document chunks for file_id {file_id}")

        vectorstore._collection.delete(where={"file_id": file_id})
        print(f"Deleted all documents with file_id {file_id}")

        return True
    
    except Exception as e:
        print(f"Error deleting document with file_id {file_id} from Chroma: {str(e)}")
        return False