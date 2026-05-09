from sqlalchemy import Column, Index, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from app.core.database import Base
import uuid

class UserResume(Base):
    __tablename__ = "user_resumes"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    resume_id = Column(UUID(as_uuid=True), ForeignKey("resumes.id", ondelete="CASCADE"), nullable=False)

    __table_args__ = (
        Index("idx_user_resumes_user_id", "user_id"),
        Index("idx_user_resumes_resume_id", "resume_id")
    )
