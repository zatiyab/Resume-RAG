# backend/app/core/config.py (UPDATED & CONSOLIDATED)
import os
from dotenv import load_dotenv
from langchain_cohere import ChatCohere

load_dotenv() # Load environment variables from .env

class Settings:
    # Database URL for PostgreSQL (from previous step)
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://hiremind_user:hiremind_password@localhost:5432/hiremind_db")
    
    # Secret key for JWT authentication (from previous step)
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your_super_secret_jwt_key_that_is_very_long_and_random")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30 # Token expiry time in minutes

    # Qdrant URL (from your previous backend structure)
    QDRANT_URL: str = os.getenv("QDRANT_URL", "http://localhost:6333")

    # Cohere API Key (from your previous backend structure)
    COHERE_API_KEY: str = os.getenv("COHERE_API_KEY")

    # Google API Key (for metadata filtering, from your previous backend structure)
    GOOGLE_API_KEY: str = os.getenv("GOOGLE_API_KEY")

    # Allowed Origins for CORS (from your provided config.py)
    # Example: "http://localhost:5173,http://yourfrontend.com"
    ALLOWED_ORIGINS: list[str] = os.getenv("ALLOWED_ORIGINS", "http://localhost:5173").split(",")
    # Note: If ALLOWED_ORIGINS is a comma-separated string in .env, .split(",") will make it a list.

settings = Settings()