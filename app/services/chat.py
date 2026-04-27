from app.rag_logic.rag_main import main
from app.crud.db_crud import add_chat,add_history
import uuid
import json


async def post_chat_messages(data,db):
    user_id = data.user_id
    user_query = data.user_query
    # If the frontend passes 'default' or None, create a fresh chat_id UUID for this invocation
    chat_id = data.chat_id if data.chat_id and data.chat_id != "default" else str(uuid.uuid4())
    k = data.k
    print(data)
    
    add_chat(user_id=user_id,role="user",content=user_query,chat_id=chat_id,db=db)
    main_result = main(k,user_query,None,user_id,db)
    response = main_result["result"]
    history = main_result["history"]
    source_docs = main_result["selected_files"]
    
    # We no longer pass hist_id, allowing the DB to generate its own UUID
    add_history(user_id=user_id,history=history,db=db)
    add_chat(user_id=user_id,role="assistant",content=response,chat_id=str(uuid.uuid4()),db=db)
    
    return {"status":"success",
    "user_id":user_id,
    "selected_files":source_docs,
    "response":response}


async def get_resumes_zip(req):
    print(req)

async def upload_all_resumes(req):
    print(req)
    print(req.files)