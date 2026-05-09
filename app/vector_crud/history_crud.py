from app.clients import get_qdrant
import datetime
from qdrant_client.models import PointStruct

from app.services.qdrant_client import _embed_text
from app.core.logger import logger

qdrant_client = get_qdrant()


def add_history(history_text: str, hist_id, user_id,chat_group_id):
    '''
    Get history for the LLM chatbot and converts it into a vector
    and also add it to the vector history db and prints the result of the upsert operation
    '''
    import uuid
    if not hist_id:
        hist_id = str(uuid.uuid4())

    vector = _embed_text(history_text.lower())
    point = PointStruct(id=hist_id, vector=vector, payload={"created_at": datetime.datetime.utcnow().isoformat(),
                       'history':history_text,
                       'user_id':user_id,
                       'chat_group_id': chat_group_id})
    operation_info = qdrant_client.upsert(
            collection_name="history",
            wait=True,
            points=[point]
        )

    logger.debug(f"--- DEBUG: History Added: {operation_info} ---")

def delete_history(hist_id):
    '''
    Deletes a history entry from the vector history db based on hist_id and prints the result of the delete operation
    '''
    operation_info = qdrant_client.delete(
        collection_name="history",
        points_selector=hist_id
    )
    logger.debug(f"--- DEBUG: History Deleted: {operation_info} ---")

def delete_history_by_user_id(user_id):
    '''
    Deletes all history entries for a user from the vector history db based on user_id and prints the result of the delete operation
    '''
    from qdrant_client.models import Filter, FieldCondition, MatchValue
    user_filter = Filter(
        must=[FieldCondition(key="user_id", match=MatchValue(value=user_id))]
    )
    operation_info = qdrant_client.delete(
        collection_name="history",
        points_selector=user_filter
    )
    logger.debug(f"--- DEBUG: History Deleted for user {user_id}: {operation_info} ---")

def get_similar_history(user_id, chat_group_id,user_query, k=5):
    '''
    Retrieves all history entries for a user and chat group from the vector history db based on user_id and chat_group_id and returns a list of history texts
    '''
    from qdrant_client.models import Filter, FieldCondition, MatchValue
    query_embedding = _embed_text(user_query.lower(), input_type="search_query")

            
    user_chat_filter = Filter(
        must=[
            FieldCondition(key="user_id", match=MatchValue(value=user_id)),
            FieldCondition(key="chat_group_id", match=MatchValue(value=chat_group_id))
        ]
    )
    results = qdrant_client.query_points(
        collection_name='history',
        query=query_embedding,
        limit=k,
        query_filter=user_chat_filter
    )
    return [
        point.payload.get("history")
        for point in (results.points or [])
        if point.payload and point.payload.get("history")
    ]

def delete_history_by_chat_group_id(user_id, chat_group_id):
    '''
    Deletes all history entries for a user and chat group from the vector history db based on user_id and chat_group_id and prints the result of the delete operation
    '''
    from qdrant_client.models import Filter, FieldCondition, MatchValue
    user_chat_filter = Filter(
        must=[
            FieldCondition(key="user_id", match=MatchValue(value=str(user_id))),
            FieldCondition(key="chat_group_id", match=MatchValue(value=str(chat_group_id)))
        ]
    )
    operation_info = qdrant_client.delete(
        collection_name="history",
        points_selector=user_chat_filter
    )
    logger.debug(f"--- DEBUG: History Deleted for user {user_id} and chat group {chat_group_id}: {operation_info} ---")