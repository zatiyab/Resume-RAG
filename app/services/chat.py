from app.rag_logic.rag_main import main
from app.crud.db_crud import add_chat,add_history
import uuid
import json

hist_id = 1
async def post_chat_messages(data,db):
    global hist_id
    user_id = data.user_id
    user_query = data.user_query
    k = data.k
    print(data)
    add_chat(user_id=user_id,role="user",content=user_query,session_id="c9a30aef-dbf9-48f3-9a5f-1e6ce90a9f52",db=db)
    response, history, zip_buffer ,source_docs = main(k,user_query,hist_id,user_id,db)
    add_history(user_id=user_id,history=history,db = db)
    add_chat(user_id=user_id,role="assistant",content=response,session_id="c9a30aef-dbf9-48f3-9a5f-1e6ce90a9f52",db=db)
    hist_id+=1
    return {"status":"success",
    "user_id":user_id,
    "selected_files":source_docs,
    "zip_file":zip_buffer,
    "response":response}


async def get_resumes_zip(req):
    print(req)

async def upload_all_resumes(req):
    print(req)
    print(req.files)