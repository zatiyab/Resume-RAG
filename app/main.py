# backend/app/main.py (UPDATED for Sync DB with FastAPI)
from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session # Import synchronous Session
# from sqlalchemy.ext.asyncio import AsyncSession # No longer needed
from app.core.database import create_all_tables_sync, get_db # Import sync get_db and table creation
from app.core.config import settings
from app.api.routes import auth_router


import asyncio

# FastAPI Lifespan Context Manager
@asynccontextmanager
async def lifespan(app: FastAPI):
    print("FastAPI application startup event: Initializing services and creating tables...")
    global llm, embedding, qdrant_client
    try:
        await asyncio.to_thread(create_all_tables_sync) # <--- Use asyncio.to_thread
        print("Database tables created/checked synchronously during startup.")
    except Exception as e:
        print(f"Error creating database tables at startup: {e}")
    
    yield

    print("FastAPI application shutdown event.")

# FastAPI App instance
app = FastAPI(
    title="HireMind Backend API",
    description="RAG-based AI Resume Assistant Backend powered by FastAPI",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[str(origin) for origin in settings.ALLOWED_ORIGINS],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Root Endpoint (Test) ---
@app.get("/")
async def read_root():
    return {"message": "Hello, HireMind Backend (FastAPI) is running!"}

# --- Register API Routers ---
app.include_router(auth_router, prefix="/api/v1/auth", tags=["Auth"])