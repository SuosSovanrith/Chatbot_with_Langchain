from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.chains import create_history_aware_retriever, create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from typing import List
from langchain_core.documents import Document
from chroma_utils import vectorstore
from dotenv import load_dotenv
import os

# set api key enviroment
load_dotenv()
if not os.environ.get("OPENAI_API_KEY"):
    os.environ["OPENAI_API_KEY"] = os.getenv('OPENAI_API_KEY')

# Fetch relevant document chunks based on the user's query.
retriever = vectorstore.as_retriever(search_kwargs={"k": 2}) # return the top 2 most similar documents

# StrOutputParser is used for processing the language model's output.
output_parser = StrOutputParser()

# Setting up prompts

# Recreate the user's input question based on chat history.
contextualize_q_system_prompt = (
    "Given a chat history and the latest user question "
    "which might reference context in the chat history, "
    "formulate a standalone question which can be understood "
    "without the chat history. Do NOT answer the question, "
    "just reformulate it if needed and otherwise return it as is."
)

contextualize_q_prompt = ChatPromptTemplate.from_messages([
    ("system", contextualize_q_system_prompt),
    MessagesPlaceholder("chat_history"),
    ("human", "{input}"),
])

# Gnerate the final answer based on the retrieved context and chat history.
qa_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a helpful AI assistant. Use the following context to answer the user's question."),
    ("system", "Context: {context}"),
    MessagesPlaceholder(variable_name="chat_history"),
    ("human", "{input}")
])


# Create main rag chain
def get_rag_chain(model="gpt-4o-mini"):
    # Initialize out ai model
    llm = ChatOpenAI(model=model)
    
    # Creates a retriever that can understand context from previous chats.
    history_aware_retriever = create_history_aware_retriever(llm, retriever, contextualize_q_prompt)
    
    # Create the chain for answering questions from the list of documents
    question_answer_chain = create_stuff_documents_chain(llm, qa_prompt)
    
    # Create and return our main rag chain 
    rag_chain = create_retrieval_chain(history_aware_retriever, question_answer_chain)    
    return rag_chain