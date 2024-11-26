# Chatbot_with_Langchain

This project is a multi-user chatbot that allows users to upload documents (PDF, DOCX, HTML, HTM) and ask context-aware questions about them. The chatbot maintains conversation history and provides intelligent, conversational responses.

---

## Features

- **Document Upload**: Supports PDF and DOCX formats.
- **Context-Aware Question Answering**: Answers questions based on the uploaded document's content.
- **Conversational Responses**: Maintains chat history for seamless conversations.
- **Multi-User Support**: Handles multiple users simultaneously with session ID.

---

## Technologies and Tools

- **Frameworks**:  
  - [FastAPI](https://fastapi.tiangolo.com/) - Backend for API development.
  - [Streamlit](https://streamlit.io/) - Frontend interface for users.

- **AI Model**:  
  - [GPT-3.5-Turbo](https://platform.openai.com/docs/models/gpt-3-5) (default, Free Tier)  
  - Supports GPT-4o and GPT-4o-mini for more advanced performance.

- **Libraries**:  
  - **Document Processing**: `pypdf`, `docx2txt`
  - **Vector Database**: [ChromaDB](https://www.trychroma.com/)
  - **LangChain**: To manage prompt engineering and context handling.
  - **Web Server**: `uvicorn`

---

## Setup Instructions

### Prerequisites

1. **Python 3.8+**: Install [Python](https://www.python.org/downloads/).
2. **OpenAI API Key**: Get your key from [OpenAI](https://platform.openai.com/api-keys).

---

### Installation

1. Clone the repository:  
    ```
    git clone https://github.com/SuosSovanrith/Chatbot_with_Langchain.git
    cd Chatbot_with_Langchain

2. Install necessary packages using pip:
    ```
    pip install -r requirements.txt

3. vCreate a .env file in the project root using the sample:
    ```
    cp .env.example .env

4. Fill in the .env file with your API key and other configurations:
    ```
    OPENAI_API_KEY=your_openai_api_key

5. Start the backend server in termal:
    ```
    cd api
    uvicorn main:fapi --reload

**Note:** fapi is the name of the FastApi varable declared in main.py. It is usually named app, but that depend on you

6. Launch the Streamlit frontend in terminal:
    ```
    cd app
    streamlit run steamlit_app.py
