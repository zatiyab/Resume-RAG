# backend/app/core/database.py (UPDATED for Synchronous Engine)
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.orm import declarative_base
from sqlalchemy.pool import NullPool # Still use NullPool for connection management
from app.core.config import settings
from typing import Generator # Use Generator for sync get_db

# Create the SQLAlchemy synchronous engine
# Use psycopg2 as the driver (implicitly by default with postgresql://)
engine = create_engine(
    settings.DATABASE_URL,
    echo=False, # Set to True for SQL logs if needed for debugging
    poolclass=NullPool, # Still good practice for external poolers like pgbouncer
    # connect_args={"statement_cache_size": 0} - This was for asyncpg, no longer needed here
    pool_recycle=3600 # Good practice for long-lived applications
)

# Create a SessionLocal class for synchronous sessions
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create a Base class for declarative models
Base = declarative_base()

# Dependency to get the synchronous database session for FastAPI (will be run in threadpool)
def get_db() -> Generator[Session, None, None]: # Use Generator for sync
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close() # Close sync session

# Function to create all tables synchronously
def create_all_tables_sync(): # Renamed to sync
    Base.metadata.create_all(bind=engine)