from app.core.logger import logger
from app.rag_logic.rag_main import main
from app.crud.chat_crud import add_chat as add_chat_to_db,add_history as add_history_to_db
import uuid


async def post_chat_messages(data,db):
    user_id = data.user_id
    user_query = data.user_query
    # If the frontend passes 'default' or None, create a fresh chat_group_id UUID for this invocation
    chat_group_id = data.chat_group_id if data.chat_group_id and data.chat_group_id != "default" else str(uuid.uuid4())
    k = data.k
    logger.info(data)
    
    add_chat_to_db(user_id=user_id,role="user",content=user_query,chat_group_id=chat_group_id,db=db)
    # Pass chat_group_id into main so history retrieval is scoped per chat group
    main_result = main(k, user_query, None, user_id, db, chat_group_id=chat_group_id)
    response = main_result.get("result", "Sorry, I couldn't generate a response.")
    history = main_result.get("history", "")
    source_docs = main_result.get("selected_files", [])
    summarized_history = main_result.get("summarized_history", "")
    # We no longer pass hist_id, allowing the DB to generate its own UUID
    # Store history with the chat_group_id so future retrievals are scoped
    add_history_to_db(user_id=user_id,history=history,db=db,chat_group_id=chat_group_id,summarized_history=summarized_history)
    add_chat_to_db(user_id=user_id,role="assistant",content=response,chat_group_id=chat_group_id,db=db)
    
    return {"status":"success",
    "user_id":user_id,
    "chat_group_id":chat_group_id,
    "selected_files":source_docs,
    "response":response}


