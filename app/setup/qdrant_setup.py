"""Qdrant vector database setup and initialization logic."""

from qdrant_client.http.models import Distance, VectorParams, HnswConfigDiff
from qdrant_client.http import models as rest
from app.clients import get_qdrant
from app.core.logger import logger


qdrant_client = get_qdrant()


def ensure_collection(collection_name: str, vectors_config: VectorParams) -> None:
    """Create a Qdrant collection if it doesn't already exist.
    
    Args:
        collection_name: Name of the collection to create.
        vectors_config: Vector configuration for the collection.
        
    Raises:
        RuntimeError: If Qdrant client is not initialized or connection fails.
    """
    if qdrant_client is None:
        raise RuntimeError("Qdrant client is not initialized.")
        
    try:
        qdrant_client.create_collection(
            collection_name=collection_name,
            vectors_config=vectors_config,
        )
    except Exception as exc:
        message = str(exc).lower()
        if "already exists" in message or "409" in message:
            logger.info("--- Qdrant collection '%s' already exists; skipping creation ---", collection_name)
            return
        raise


def ensure_payload_index(collection_name: str, field_name: str, field_schema) -> None:
    """Create a payload index on a Qdrant collection if it doesn't already exist.
    
    Args:
        collection_name: Name of the collection.
        field_name: Name of the field to index.
        field_schema: Schema type for the field.
        
    Raises:
        RuntimeError: If Qdrant client is not initialized.
    """
    if qdrant_client is None:
        raise RuntimeError("Qdrant client is not initialized.")
        
    try:
        qdrant_client.create_payload_index(
            collection_name=collection_name,
            field_name=field_name,
            field_schema=field_schema,
        )
    except Exception as exc:
        message = str(exc).lower()
        if "already exists" in message or "409" in message:
            logger.info(
                "--- Qdrant payload index '%s' on '%s' already exists; skipping creation ---",
                field_name,
                collection_name,
            )
            return
        raise


def initialize_app_data():
    """Initialize Qdrant collections and payload indexes for the application.
    
    Creates 'resumes' and 'history' collections with appropriate vector configurations
    and payload indexes. Handles race conditions where multiple workers attempt
    initialization simultaneously.
    
    Raises:
        RuntimeError: If Qdrant client is not initialized.
    """
    from app.core.config import settings
    
    logger.info("--- Initializing collections and data... ---")
    logger.info("Qdrant URL: %s", settings.QDRANT_URL if qdrant_client else "Qdrant client not initialized")
    
    if qdrant_client is None:
        raise RuntimeError("Qdrant qdrant_client is not initialized. Check QDRANT_URL, QDRANT_API_KEY and network connectivity.")

    logger.info("Qdrant Collections: %s", qdrant_client.get_collections())

    # Initialize 'resumes' collection
    if not qdrant_client.collection_exists("resumes"):
        logger.info("--- Creating 'resumes' collection ---")
        ensure_collection(
            "resumes",
            VectorParams(
                size=1536,
                distance=Distance.COSINE,
                hnsw_config=HnswConfigDiff(m=16, ef_construct=128, full_scan_threshold=10000),
                on_disk=False,
            ),
        )

        ensure_payload_index(
            collection_name="resumes",
            field_name="source",
            field_schema=rest.PayloadSchemaType.KEYWORD,
        )
        
    # Initialize 'history' collection
    if not qdrant_client.collection_exists("history"):
        logger.info("--- Creating 'history' collection ---")
        ensure_collection(
            "history",
            VectorParams(size=1536, distance=Distance.COSINE, on_disk=False),
        )
        # Create payload index for user_id so filters/deletes by user_id are supported
        try:
            ensure_payload_index(
                collection_name="history",
                field_name="user_id",
                field_schema=rest.PayloadSchemaType.KEYWORD,
            )
            ensure_payload_index(
                collection_name="history",
                field_name="chat_group_id",
                field_schema=rest.PayloadSchemaType.KEYWORD,
            )
            logger.info("Created payload index 'user_id' and 'chat_group_id' on 'history' collection")
        except Exception as e:
            logger.error(f"Warning: failed to create payload index for history.user_id and/or history.chat_group_id: {e}")
    
    logger.info("--- Initial app data setup complete. ---")

if __name__ == "__main__":
    initialize_app_data()