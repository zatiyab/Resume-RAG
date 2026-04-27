from app.models.tables import Chat,History

def add_history(user_id,history,db,hist_id=None):
    if hist_id:
        history_record = History(user_id=user_id, history=history, hist_id=hist_id)
    else:
        history_record = History(user_id=user_id, history=history)
    
    db.add(history_record)
    db.commit()
    db.refresh(history_record)
    return history_record

def add_chat(user_id,role,content,db,chat_id=None):
    if chat_id:
        chat_record = Chat(user_id=user_id, content=content, role=role, chat_id=chat_id)
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
