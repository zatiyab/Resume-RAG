# backend/app/main.py (UPDATED - Fix yield from in get_db_dependency)
from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session # Import synchronous Session
from app.core.database import create_all_tables_sync, get_db, get_engine, get_session_local # Get core DB components
from app.core.config import settings
from core.database import SessionLocal
from typing import Generator # For synchronous dependency


from app.api.routes import auth_router 


import asyncio # For asyncio.to_thread
from fastapi.concurrency import run_in_threadpool #


# FastAPI Lifespan Context Manager
@asynccontextmanager
async def lifespan(app: FastAPI):
    print("FastAPI application startup event: Initializing services and creating tables...")
    

    # Initialize Engine and SessionLocal within lifespan and attach to app.state
    app.state.engine = get_engine()
    app.state.SessionLocal = get_session_local(app.state.engine)

    try:
        await asyncio.to_thread(create_all_tables_sync, app.state.engine)
        print("Database tables created/checked synchronously during startup.")
    except Exception as e:
        print(f"Error creating database tables at startup: {e}")
    
    yield

    # Shutdown Event Logic
    print("FastAPI application shutdown event.")
    if app.state.engine:
        app.state.engine.dispose() # Dispose engine connections on shutdown
        print("Database engine disposed.")


# FastAPI App instance
app = FastAPI(
    title="HireMind Backend API",
    description="RAG-based AI Resume Assistant Backend powered by FastAPI",
    version="1.0.0",
    lifespan=lifespan, # Attach the lifespan context manager
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[str(origin) for origin in settings.ALLOWED_ORIGINS],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


async def get_db_dependency(db_session_local: type[SessionLocal] = Depends(lambda: app.state.SessionLocal)) -> Generator[Session, None, None]:
  
    db = db_session_local() # Get a synchronous session
    try:
        yield db # Yield the synchronous session
    finally:

        await run_in_threadpool(db.close) 
  


app.dependency_overrides[get_db] = get_db_dependency


# --- Root Endpoint (Test) ---
@app.get("/")
async def read_root():
    return {"message": "Hello, HireMind Backend (FastAPI) is running!"}

# --- Register API Routers ---
app.include_router(auth_router, prefix="/api/v1/auth", tags=["Auth"])