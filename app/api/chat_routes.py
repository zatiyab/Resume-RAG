from app.core.logger import logger

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.crud.chat_crud import get_chat_history, get_chat_groups, delete_chat_group as delete_chat_group_from_db

from app.schemas.req_models import ChatPost

from app.services.auth_service import AuthService
from app.services.chat import post_chat_messages

from app.api.dependencies import get_current_user_id, get_db_with_retry


router = APIRouter()



@router.get("/chat/history/{user_id}")
async def get_chat_history_endpoint(user_id: str, limit: int = 5, offset: int = 0, chat_group_id: str | None = None, db: Session = Depends(get_db_with_retry), current_user_id: str = Depends(get_current_user_id)):
    """
    Get paginated chat history for a user.
    
    Query Parameters:
    - limit: Number of messages to fetch (default 5, max 50)
    - offset: Number of messages to skip (default 0)
    
    Returns:
    {
        "messages": [...],
        "total": total_message_count,
        "offset": current_offset,
        "limit": current_limit,
        "hasMore": bool
    }
    """
    from uuid import UUID
    
    # Verify the user is accessing their own history
    if user_id != current_user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User ID mismatch. Cannot access chat history for another user."
        )
    
    try:
        # Validate limit to prevent abuse
        limit = min(limit, 50) if limit > 0 else 5
        offset = max(offset, 0)
        
        user_uuid = UUID(user_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid user_id format")
    
    try:
        history_data = get_chat_history(user_uuid, limit=limit, offset=offset, db=db, chat_group_id=chat_group_id)
        history_data["hasMore"] = (offset + limit) < history_data["total"]
        return history_data
    except Exception as e:
        logger.error(f"Error fetching chat history for user {user_id}: {e}")
        raise HTTPException(status_code=500, detail="Error retrieving chat history")


@router.get("/chat/groups/{user_id}")
async def get_chat_groups_endpoint(user_id: str, db: Session = Depends(get_db_with_retry), current_user_id: str = Depends(get_current_user_id)):
    from uuid import UUID
    
    if user_id != current_user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User ID mismatch. Cannot access chat groups for another user."
        )

    try:
        user_uuid = UUID(user_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid user_id format")

    try:
        return {"groups": get_chat_groups(user_uuid, db=db)}
    except Exception as e:
        logger.error(f"Error fetching chat groups for user {user_id}: {e}")
        raise HTTPException(status_code=500, detail="Error retrieving chat groups")





@router.post("/chat")
async def post_chat(request: ChatPost, db: Session = Depends(get_db_with_retry), current_user_id: str = Depends(get_current_user_id)):
    # Verify the user_id in the request matches the authenticated user
    if str(request.user_id) != current_user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User ID mismatch. Cannot access chat for another user."
        )
    return await post_chat_messages(request, db)



@router.delete("/chat/groups/{user_id}/{chat_group_id}")
async def delete_chat_group_endpoint(
    user_id: str,
    chat_group_id: str,
    db: Session = Depends(get_db_with_retry),
    current_user_id: str = Depends(get_current_user_id),
):
    from uuid import UUID

    if user_id != current_user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User ID mismatch. Cannot delete chat groups for another user."
        )

    try:
        user_uuid = UUID(user_id)
        group_uuid = UUID(chat_group_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid user_id or chat_group_id format")

    try:
        from app.vector_crud.history_crud import delete_history_by_chat_group_id as delete_history_by_chat_group_id_from_qdrant
        # Delete from Qdrant vector store
        delete_history_by_chat_group_id_from_qdrant(user_uuid, group_uuid)
        # Delete from SQL database
        return delete_chat_group_from_db(user_uuid, group_uuid, db=db)
    except Exception as e:
        logger.error(f"Error deleting chat group {chat_group_id} for user {user_id}: {e}")
        raise HTTPException(status_code=500, detail="Error deleting chat group")



