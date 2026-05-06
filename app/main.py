from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.chat_routes import router as chat_router
from app.api.auth_routes import router as auth_router   
from app.api.resume_routes import router as resume_router

from app.core.config import settings
from app.services.qdrant_client import initialize_app_data

# FastAPI Lifespan Context Manager
@asynccontextmanager
async def lifespan(app: FastAPI):
    initialize_app_data()  # Initialize collections and data on startup
    print("FastAPI application startup event: Initializing services...")
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
app.include_router(chat_router,tags=["Chat"])
app.include_router(auth_router,tags=["Authentication"])
app.include_router(resume_router,tags=["Resume"])