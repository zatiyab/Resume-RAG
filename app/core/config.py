import os
from dotenv import load_dotenv
from langchain_cohere import ChatCohere

load_dotenv()

llm = ChatCohere(
    model="command-r-plus-08-2024",
    timeout_seconds=60,
    cohere_api_key=os.getenv("COHERE_API_KEY"),
)


class Settings:
    COHERE_API_KEY: str = os.getenv("COHERE_API_KEY")

    DATABASE_URL: str = os.getenv("DB_URL")

    SECRET_KEY: str = os.getenv("SECRET_KEY", "your_super_secret_jwt_key_that_is_very_long_and_random")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    QDRANT_URL: str = os.getenv("QDRANT_URL")
    QDRANT_API_KEY: str = os.getenv("QDRANT_API_KEY")

    SUPABASE_URL: str = os.getenv("SUPABASE_URL")
    SUPABASE_KEY: str = os.getenv("SUPABASE_KEY")

    ALLOWED_ORIGINS: list[str] = os.getenv("ALLOWED_ORIGINS", "http://localhost:5173").split(",")


settings = Settings()