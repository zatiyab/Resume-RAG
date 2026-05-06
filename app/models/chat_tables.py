import uuid
from datetime import datetime
from sqlalchemy import Column, Integer, Text, DateTime, Index, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from app.core.database import Base

class Chat(Base):
    __tablename__ = "chats"

    chat_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    chat_group_id = Column(UUID(as_uuid=True), nullable=False)
    created_at = Column(DateTime(timezone=True),default=datetime.utcnow)
    role = Column(Text, nullable=False)        # e.g., 'user' or 'assistant'
    content = Column(Text, nullable=False)     # actual message

    __table_args__ = (
        Index("idx_chats_user_id", "user_id"),
        Index("idx_chats_chat_group_id", "chat_group_id"),
    )


class History(Base):
    __tablename__ = "history"
    
    user_id = Column(UUID(as_uuid=True),ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    hist_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    created_at = Column(DateTime(timezone=True),default=datetime.utcnow)
    history = Column(Text, nullable=False)     # entire history content (e.g., summarized or full)
    chat_group_id = Column(UUID(as_uuid=True), nullable=True)  # Optional link to a chat group
    __table_args__ = (
        Index("idx_history_user_id", "user_id"),
        Index("idx_history_chat_group_id", "chat_group_id"),
    )
