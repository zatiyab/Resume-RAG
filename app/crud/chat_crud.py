from sqlalchemy import func

from app.models.chat_tables import Chat, History
from app.models.resumes import Resume
from app.models.user_resumes import UserResume


def get_chat_groups(user_id, db):
    latest_message_rn = func.row_number().over(
        partition_by=Chat.chat_group_id,
        order_by=Chat.created_at.desc(),
    ).label("rn")

    title_message_rn = func.row_number().over(
        partition_by=Chat.chat_group_id,
        order_by=Chat.created_at.asc(),
    ).label("rn")

    latest_messages = (
        db.query(
            Chat.chat_group_id.label("chat_group_id"),
            Chat.content.label("last_message"),
            Chat.role.label("last_message_role"),
            Chat.created_at.label("last_message_at"),
            latest_message_rn,
        )
        .filter(Chat.user_id == user_id)
        .subquery()
    )

    first_user_messages = (
        db.query(
            Chat.chat_group_id.label("chat_group_id"),
            Chat.content.label("title"),
            title_message_rn,
        )
        .filter(Chat.user_id == user_id, Chat.role == "user")
        .subquery()
    )

    message_counts = (
        db.query(
            Chat.chat_group_id.label("chat_group_id"),
            func.count(Chat.chat_id).label("message_count"),
        )
        .filter(Chat.user_id == user_id)
        .group_by(Chat.chat_group_id)
        .subquery()
    )

    rows = (
        db.query(
            latest_messages.c.chat_group_id,
            latest_messages.c.last_message,
            latest_messages.c.last_message_role,
            latest_messages.c.last_message_at,
            message_counts.c.message_count,
            first_user_messages.c.title,
        )
        .join(message_counts, message_counts.c.chat_group_id == latest_messages.c.chat_group_id)
        .outerjoin(
            first_user_messages,
            (first_user_messages.c.chat_group_id == latest_messages.c.chat_group_id)
            & (first_user_messages.c.rn == 1),
        )
        .filter(latest_messages.c.rn == 1)
        .order_by(latest_messages.c.last_message_at.desc())
        .all()
    )

    grouped_sessions = []
    for row in rows:
        preview = row.last_message.strip() if row.last_message else "New chat"
        grouped_sessions.append(
            {
                "chat_group_id": str(row.chat_group_id),
                "title": (row.title or preview or "New chat")[:48],
                "last_message": row.last_message or "",
                "last_message_role": row.last_message_role,
                "last_message_at": row.last_message_at.isoformat() if row.last_message_at else None,
                "message_count": row.message_count,
            }
        )

    return grouped_sessions

def add_history(user_id,history,db,chat_group_id,hist_id=None,summarized_history=None):
    if hist_id:
        history_record = History(user_id=user_id, history=history, hist_id=hist_id, chat_group_id=chat_group_id, summarized_history=summarized_history)
    else:
        history_record = History(user_id=user_id, history=history, chat_group_id=chat_group_id, summarized_history=summarized_history)
    
    db.add(history_record)
    db.commit()
    db.refresh(history_record)
    return history_record

def add_chat(user_id,role,content,db,chat_group_id=None):
    if chat_group_id:
        chat_record = Chat(user_id=user_id, content=content, role=role, chat_group_id=chat_group_id)
    else:
        chat_record = Chat(user_id=user_id, content=content, role=role)
        
    db.add(chat_record)
    db.commit()
    db.refresh(chat_record)
    return chat_record


def get_last_history(user_id, db):
    return (
        db.query(History.history)
        .filter(History.user_id == user_id)
        .order_by(History.created_at.desc())
        .first()  # instead of limit(1)
    )

def get_last_k_history(user_id,chat_group_id, db, k=2):
    """
    Get the last K history entries for a user (most recent first).
    Used for pronoun resolution and conversation context.
    
    Args:
        user_id: User's UUID
        chat_group_id: Chat group UUID
        db: Database session
        k: Number of recent history entries to retrieve (default 2)
    
    Returns:
        List of history strings, ordered from most recent to oldest
    """
    histories = (
        db.query(History.history)
        .filter(History.user_id == user_id).filter(History.chat_group_id == chat_group_id)  
        .order_by(History.created_at.desc())
        .limit(k)
        .all()
    )
    
    # Extract history text from tuples and reverse to chronological order
    return [h[0] for h in reversed(histories)] if histories else []


def get_chat_history(user_id, limit=5, offset=0, db=None, chat_group_id=None):
    """
    Get paginated chat history for a user.
    Returns messages ordered from newest to oldest, but reversed for chronological display.
    
    Args:
        user_id: User's UUID
        limit: Number of messages to fetch (default 5)
        offset: Number of messages to skip (default 0)
        db: Database session
        chat_group_id: Optional chat group ID to filter by
    
    """
    query = db.query(Chat).filter(Chat.user_id == user_id)
    if chat_group_id:
        query = query.filter(Chat.chat_group_id == chat_group_id)

    messages = (
        query
        .order_by(Chat.created_at.desc())  # Newest first for pagination
        .offset(offset)
        .limit(limit)
        .all()
    )

    total_count = query.count()
        # Reverse to display chronologically (oldest first in UI)
    
    return {
        "messages": [
            {
                "chat_id": str(msg.chat_id),
                "chat_group_id": str(msg.chat_group_id),
                "role": msg.role,
                "content": msg.content,
                "created_at": msg.created_at.isoformat()
            }
            for msg in reversed(messages)
        ],
        "total": total_count,
        "offset": offset,
        "limit": limit
    }


def delete_chat_history(user_id, db):
    db.query(Chat).filter(Chat.user_id == user_id).delete()
    db.query(History).filter(History.user_id == user_id).delete()
    db.commit()
    return {"message": "Chat history deleted successfully."}

def delete_chat_group_history(user_id, chat_group_id, db):
    """
    Delete all chat history entries for a specific chat group.
    Args:
        user_id: User's UUID
        chat_group_id: Chat group UUID
        db: Database session
    Returns:
        Dict with deletion status
    """
    
    deleted_count = db.query(History).filter(History.user_id == user_id, History.chat_group_id == chat_group_id).delete()
    db.commit()
    return {"message": f"Chat group {chat_group_id} history deleted successfully.", "deleted_entries": deleted_count}

def delete_chat_group_chat(user_id, chat_group_id, db):
    """
    Delete a single chat group and all of its messages for a user.

    Args:
        user_id: User's UUID
        chat_group_id: Chat group UUID
        db: Database session

    Returns:
        Dict with deletion status and removed row count
    """
    deleted_count = (
        db.query(Chat)
        .filter(Chat.user_id == user_id)
        .filter(Chat.chat_group_id == chat_group_id)
        .delete(synchronize_session=False)
    )
    db.commit()
    return {
        "message": "Chat group deleted successfully.",
        "deleted_messages": deleted_count,
        "chat_group_id": str(chat_group_id),
    }

def delete_chat_group(user_id, chat_group_id, db):
    """
    Delete a single chat group and all of its messages for a user.

    Args:
        user_id: User's UUID
        chat_group_id: Chat group UUID
        db: Database session
    Returns:
        Dict with deletion status and removed row count
    """
    response1 = delete_chat_group_chat(user_id, chat_group_id, db)
    response2 = delete_chat_group_history(user_id, chat_group_id, db)
    return {
        "message": f"Chat group {chat_group_id} and its history deleted successfully.",
        "deleted_messages": response1.get("deleted_messages", 0),
        "chat_group_id": str(chat_group_id),
        "deleted_history_entries": response2.get("deleted_entries", 0)
    }