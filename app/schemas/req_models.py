from pydantic import BaseModel
from typing import List,Dict,Any, Optional

class ChatPost(BaseModel):
    user_id:str
    user_query:str
    chat_group_id: Optional[str] = "default"
    k:Optional[int] = 5
    # history:Optional[List[Dict[str,str]] ] = None

class ChatResponse(BaseModel):
    response:str
    source_docs:List[str]

class DownloadRequest(BaseModel):
    files: list[str]
    user_id: str