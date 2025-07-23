from app.models.tables import Chat,History

def add_history(user_id,history,db):
    history_record = History(
        user_id = user_id,
        session_id = "c9a30aef-dbf9-48f3-9a5f-1e6ce90a9f52",
        history = history
    )
    db.add(history_record)
    db.commit()
    db.refresh(history_record)
    return history_record

def add_chat(user_id,role,content,session_id,db):
    chat_record = Chat(
        user_id = user_id,
        content = content,
        role = role,
        session_id = "c9a30aef-dbf9-48f3-9a5f-1e6ce90a9f52")
    db.add(chat_record)
    db.commit()
    db.refresh(chat_record)
    return chat_record

