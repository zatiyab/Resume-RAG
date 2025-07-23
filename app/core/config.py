import os
from dotenv import load_dotenv
from qdrant_client import QdrantClient
from langchain.embeddings import HuggingFaceEmbeddings
from langchain_cohere import ChatCohere


# LLM
llm = ChatCohere(model="command-r-plus", timeout_seconds=60, cohere_api_key='BCxkxzdkBAiA9Ey0mS7csgHSRxaV2YHcYu6mtTrg')


load_dotenv()

print(os.getenv("DB_URL"))
class Settings:
    COHERE_API_KEY: str = os.getenv("COHERE_API_KEY")
    DB_URL: str = os.getenv("DB_URL")
    ALLOWED_ORIGINS: list[str] = os.getenv("ALLOWED_ORIGINS", "http://localhost:8000").split(",")

settings = Settings()