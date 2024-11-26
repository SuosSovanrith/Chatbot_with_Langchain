# use pydantic library to validate data with our own defined data schema
from pydantic import BaseModel, Field
from enum import Enum
from datetime import datetime

# schema model as Enum for our available ai model
class ModelName(str, Enum):
    GPT4_O = "gpt-4o"
    GPT4_O_MINI = "gpt-4o-mini"
    GPT3_5_TURBO = "gpt-3.5-turbo"
    
# schema model for chat input
class QueryInput(BaseModel):
    question: str # required
    session_id: str = Field(default=None) # optional, if not provided, a new session_id will be created
    model: ModelName = Field(default=ModelName.GPT3_5_TURBO) # optional ai model, default to GPT3_5_TURBO because i am using free tier

# schema model for chat response
class QueryResponse(BaseModel):
    answer: str # generated response
    session_id: str # for continuing chat history
    model: ModelName # ai model used to generate response

# schema model for document's meta data
class DocumentInfo(BaseModel):
    id: int # unique id for each document
    filename: str 
    upload_timestamp: datetime

class DeleteFileRequest(BaseModel):
    file_id: int # id of the file to be deleted