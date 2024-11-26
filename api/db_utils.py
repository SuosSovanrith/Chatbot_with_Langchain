# use sqlite database for storing documents and chat history
import sqlite3
from sqlite3 import Error
import logging

# Set database name
DB_NAME = "langchainchatbot.db"

# Setting up for logging our app's info
logging.basicConfig(filename='app.log', level=logging.INFO)

# Connection to database
def get_db_connection():
    try:
        conn = sqlite3.connect(DB_NAME)
        conn.row_factory = sqlite3.Row
        return conn
    
    except Error as e:
        # print(f"Error connecting to database: {e}")
        logging.error(f"Error connecting to database: {e}")
        return None


# Create table to stores chat history and model responses into database
def create_application_logs():
    conn = None
    try:
        conn = get_db_connection()
        if conn:
            conn.execute('''CREATE TABLE IF NOT EXISTS application_logs
                            (id INTEGER PRIMARY KEY AUTOINCREMENT,
                             session_id TEXT,
                             user_query TEXT,
                             gpt_response TEXT,
                             model TEXT,
                             created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
            conn.commit()
            
    except Error as e:
        # print(f"Error creating application_logs table: {e}")
        logging.error(f"Error creating application_logs table: {e}")
        
    finally:
        if conn:
            conn.close()


# Create table to stores records of uploaded documents.
def create_document_store():
    conn = None
    try:
        conn = get_db_connection()
        if conn:
            conn.execute('''CREATE TABLE IF NOT EXISTS document_store
                            (id INTEGER PRIMARY KEY AUTOINCREMENT,
                             filename TEXT,
                             upload_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
            conn.commit()
            
    except Error as e:
        # print(f"Error creating document_store table: {e}")
        logging.error(f"Error creating document_store table: {e}")
        
    finally:
        if conn:
            conn.close()
    
    
# Insert chat logs into application_logs table
def insert_application_logs(session_id, user_query, gpt_response, model):
    conn = None
    try:
        conn = get_db_connection()
        if conn:
            conn.execute('INSERT INTO application_logs (session_id, user_query, gpt_response, model) VALUES (?, ?, ?, ?)',
                         (session_id, user_query, gpt_response, model))
            conn.commit()
            
    except Error as e:
        # print(f"Error inserting application logs: {e}")
        logging.error(f"Error inserting application logs: {e}")
        
    finally:
        if conn:
            conn.close()


# Get chat history from application_logs table
def get_chat_history(session_id):
    conn = None
    messages = []
    try:
        conn = get_db_connection()
        if conn:
            cursor = conn.cursor()
            cursor.execute('SELECT user_query, gpt_response FROM application_logs WHERE session_id = ? ORDER BY created_at', (session_id,))
            for row in cursor.fetchall():
                # formatted chat history for our RAG chain
                messages.extend([
                    {"role": "human", "content": row['user_query']},
                    {"role": "ai", "content": row['gpt_response']}
                ])
                
    except Error as e:
        # print(f"Error retrieving chat history: {e}")
        logging.error(f"Error retrieving chat history: {e}")
        
    finally:
        if conn:
            conn.close()
            
    return messages


# Inserting new document records into document_store table
def insert_document_record(filename):
    conn = None
    file_id = None
    try:
        conn = get_db_connection()
        if conn:
            cursor = conn.cursor()
            cursor.execute('INSERT INTO document_store (filename) VALUES (?)', (filename,))
            file_id = cursor.lastrowid
            conn.commit()
            
    except Error as e:
        # print(f"Error inserting document record: {e}")
        logging.error(f"Error inserting document record: {e}")
        
    finally:
        if conn:
            conn.close()
    return file_id



# Deleting document records from document_store table
def delete_document_record(file_id):
    conn = None
    try:
        conn = get_db_connection()
        if conn:
            conn.execute('DELETE FROM document_store WHERE id = ?', (file_id,))
            conn.commit()
            
    except Error as e:
        # print(f"Error deleting document record: {e}")
        logging.error(f"Error deleting document record: {e}")
        
    finally:
        if conn:
            conn.close()
            
    return True


# Get all document records from document_store table for listing
def get_all_documents():
    conn = None
    documents = []
    try:
        conn = get_db_connection()
        if conn:
            cursor = conn.cursor()
            cursor.execute('SELECT id, filename, upload_timestamp FROM document_store ORDER BY upload_timestamp DESC')
            documents = cursor.fetchall()
            
    except Error as e:
        # print(f"Error retrieving documents: {e}")
        logging.error(f"Error retrieving documents: {e}")
        
    finally:
        if conn:
            conn.close()
            
    return [dict(doc) for doc in documents]


# Initialize the database tables
create_application_logs()
create_document_store()