from fastapi import APIRouter, Request, Depends
from sqlalchemy.orm import Session
from app.schemas.req_models import ChatPost, ChatResponse
from app.services.chat import post_chat_messages
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