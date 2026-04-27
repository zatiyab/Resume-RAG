from app.crud.db_crud import add_chat,add_history
import uuid
import json
from pathlib import Path
from fastapi import UploadFile, HTTPException

hist_id = 1
async def post_chat_messages(data,db):
    from app.rag_logic.rag_main import main
    global hist_id
    user_id = data.user_id
    user_query = data.user_query
    k = data.k
    print(data)
    try:
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

    except Exception as e:
        print(f"Error occurred: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
    

async def get_resumes_zip(req):
    print(req)

async def upload_all_resumes(files: list[UploadFile]):
    if not files:
        raise HTTPException(status_code=400, detail="No files provided.")

    resumes_dir = Path("resumes")
    resumes_dir.mkdir(parents=True, exist_ok=True)

    allowed_ext = {".pdf", ".doc", ".docx"}
    saved_count = 0

    for upload in files:
        filename = Path(upload.filename or "").name
        ext = Path(filename).suffix.lower()
        if not filename or ext not in allowed_ext:
            continue

        content = await upload.read()
        if not content:
            continue

        destination = resumes_dir / filename
        destination.write_bytes(content)
        saved_count += 1

    if saved_count == 0:
        raise HTTPException(
            status_code=400,
            detail="No supported files uploaded. Please upload PDF, DOC, or DOCX."
        )

    return {
        "status": "success",
        "message": f"Uploaded {saved_count} resume(s) successfully."
    }