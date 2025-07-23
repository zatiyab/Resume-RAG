from fastapi import APIRouter, Request, Depends
from sqlalchemy.orm import Session
from app.schemas.req_models import ChatPost, ChatResponse
from app.services.chat import (post_chat_messages,
                               upload_all_resumes,
                               get_resumes_zip)
from app.core.database import SessionLocal


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


router = APIRouter()

@router.post("/chat")
async def post_chat(request:ChatPost,db:Session = Depends(get_db)):
    print(request)
    return await post_chat_messages(request,db)


@router.post("/download_resumes")
async def resumes_link(request:Request):
    return await get_resumes_zip(request)

@router.post("/upload_resumes")
async def upload_resumes(request:Request):
    return await upload_all_resumes(request)