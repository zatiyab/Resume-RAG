# backend/app/core/database.py (SIMPLIFIED & SYNCHRONOUS DB SETUP)
from sqlalchemy import create_engine, inspect # create_engine for synchronous
from sqlalchemy.orm import sessionmaker, Session, declarative_base # Session and sessionmaker for synchronous
from sqlalchemy.pool import NullPool # Still good practice for external poolers
from app.core.config import settings
from typing import Generator # For synchronous dependency

engine = create_engine(
    settings.DATABASE_URL,
    echo=False,
    poolclass=NullPool, 
    pool_recycle=3600 
)


SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_engine():
    return create_engine(
        settings.DATABASE_URL,
        echo=False,
        poolclass=NullPool,
        connect_args={
        },
        pool_recycle=3600 
    )

def get_session_local(engine_instance: create_engine): 
    return sessionmaker(autocommit=False, autoflush=False, bind=engine_instance)

def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_all_tables_sync(engine_instance):
    print("DEBUG: create_all_tables_sync called. Attempting to create tables...")
    inspector = inspect(engine_instance)
    existing_tables = inspector.get_table_names()
    if "users" not in existing_tables: 
        Base.metadata.create_all(bind=engine_instance)
        print("DEBUG: Tables created.")
    else:
        print("DEBUG: Tables already exist, skipping creation.")
    print("DEBUG: create_all_tables_sync finished.")