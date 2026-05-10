from app.core.config import settings
from qdrant_client import QdrantClient
import cohere
from functools import lru_cache
from typing import Any
from supabase import create_client
from langchain_cohere import ChatCohere

@lru_cache(maxsize=1)
def get_qdrant():
    client = None
    try:
        client = QdrantClient(url=settings.QDRANT_URL, api_key=settings.QDRANT_API_KEY)
        return client
    except Exception as e:
        client = None
        print(f"Warning: Qdrant client initialization failed: {e}")


def get_co():
    return cohere.ClientV2()


@lru_cache(maxsize=1)
def get_supabase_client() -> Any:

    """Lazily create and cache a Supabase client instance.

    Using a function avoids creating the client at import time which makes
    testing and startup ordering easier.
    """
    return create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)



def get_llm():
    llm = ChatCohere(
        model="command-r-plus-08-2024",
        timeout_seconds=60,
        cohere_api_key=settings.COHERE_API_KEY,
    )
    return llm