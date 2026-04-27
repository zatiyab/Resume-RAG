import uuid
from datetime import datetime
from sqlalchemy import Column, Text, DateTime, ForeignKey, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import declared_attr
from app.core.database import Base

class Chat(Base):
    __tablename__ = "chats"

    user_id = Column(UUID(as_uuid=True), nullable=False)
    chat_id = Column(UUID(as_uuid=True), primary_key=True)
    created_at = Column(DateTime(timezone=True),default=datetime.utcnow)
    role = Column(Text, nullable=False)        # e.g., 'user' or 'assistant'
    content = Column(Text, nullable=False)     # actual message


class History(Base):
    __tablename__ = "history"
    
    user_id = Column(UUID(as_uuid=True), nullable=False)
    hist_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    created_at = Column(DateTime(timezone=True),default=datetime.utcnow)
    history = Column(Text, nullable=False)     # entire history content (e.g., summarized or full)
