import uuid
from datetime import datetime
from sqlalchemy import Column, Integer, DateTime, Index, VARCHAR
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from app.core.database import Base

class Resume(Base):
    __tablename__ = "resumes"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    file_path = Column(VARCHAR(255), nullable=False)
    resume_name = Column(VARCHAR(255), nullable=False)
    uploaded_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    skills = Column(ARRAY(VARCHAR(255)), nullable=True)  # Array of skills
    experience_years = Column(Integer, nullable=True)  # Experience in years as text
    raw_location = Column(VARCHAR(255), nullable=True)  # Location as text
    city = Column(VARCHAR(255), nullable=True)  # City as text
    state = Column(VARCHAR(255), nullable=True)  # State as text
    domain = Column(ARRAY(VARCHAR(255)), nullable=True)  # Array of domains/industries
    name = Column(VARCHAR(255), nullable=True)  # Candidate's name as text
    resume_vector_id = Column(Integer, nullable=True)  # ID linking to vector store

    __table_args__ = (
        Index("idx_resumes_file_path", "file_path"),
    )
