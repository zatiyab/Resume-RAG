from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import router as api_router
from app.core.config import settings


# FastAPI Lifespan Context Manager
@asynccontextmanager
async def lifespan(app: FastAPI):
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
app.include_router(api_router)