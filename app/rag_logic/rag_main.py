from app.core.logger import logger
from app.services.qdrant_client import (get_relevant_docs,
                                        get_hybrid_history)
from app.setup.qdrant_setup import initialize_app_data
from app.vector_crud.history_crud import add_history
from langchain_core.runnables import RunnableMap
from langchain_core.prompts import PromptTemplate
from app.clients import get_llm
from app.rag_logic.filter import retrieve_candidates

llm = get_llm()

def main(k, user_query, hist_id, user_id, db, chat_group_id=None):
    
    logger.info(f"\nQuery: {user_query}")
    results = retrieve_candidates(user_query, db, user_id)
    logger.info(f"Found {len(results)} candidates")
    vector_ids = list(set([r.get('resume_vector_id') for r in results] ))
    logger.info(f"Candidate Vector IDs: {vector_ids}")  
     
    
    selected_files = []
    retrieved_resume_context = ""
    history_entry = ""
    initialize_app_data()
    logger.info('\n\n\n')
    logger.info('-'*100)
    logger.info("--- MAIN FUNCTION STARTED ---")

    # Store the original user input (could be JD or a regular query)
    original_user_input = user_query 
    user_query = user_query.lower()

    # --- History Retrieval for LLM (for "Conversation History" in prompt) ---
    logger.debug('--- DEBUG: Retrieving Chat History ---')

    # Use hybrid history (recent + vector-similar) for better context
    try:
        if "he" in user_query or "she" in user_query or "they" in user_query or "them" in user_query or "his" in user_query or "her" in user_query or "their" in user_query or "him" in user_query or "hers" in user_query or "theirs" in user_query:
            logger.debug("--- DEBUG: Pronouns detected in query, using hybrid history retrieval ---")
            final_history_for_llm_prompt = get_hybrid_history(
                user_query=original_user_input,
                user_id=user_id,
                db=db,
                chat_group_id=chat_group_id,
                k_recent=2,      # Last 2 recent for pronoun resolution
                k_similar=0      # Top 2 semantically similar for candidate details
            )
            logger.debug(f"--- DEBUG: Prepared History Context Length: {len(final_history_for_llm_prompt)} ---")
            final_history_for_llm_prompt = llm.invoke(f"Summarize the following conversation history but dont lose important data such as candidate information: {final_history_for_llm_prompt}").content
            
            # --- Step 2: Retrieve Relevant Resumes (for "Candidate Context" in prompt) ---
            retrieved_resume_context, selected_files = "", []
            logger.debug(f"--- DEBUG: Calling get_relevant_docs with processed query: '{user_query[:100]}' ---")
            logger.debug(f"--- DEBUG: Retrieved Resume Context Length: {len(retrieved_resume_context)} ---")


        else:
            logger.debug("--- DEBUG: No pronouns detected, using recent history retrieval ---")
            final_history_for_llm_prompt = get_hybrid_history(
                user_query=original_user_input,
                user_id=user_id,
                db=db,
                chat_group_id=chat_group_id,
                k_recent=2,      # Last 2 recent for pronoun resolution
                k_similar=1     # Top 2 semantically similar for candidate details
            )
            final_history_for_llm_prompt =llm.invoke(f"Summarize the following conversation history but dont lose important data such as candidate information: {final_history_for_llm_prompt}").content
            logger.debug(f"--- DEBUG: Prepared History Context Length: {len(final_history_for_llm_prompt)} ---")
            # --- Step 2: Retrieve Relevant Resumes (for "Candidate Context" in prompt) ---
            logger.debug(f"--- DEBUG: Calling get_relevant_docs with processed query: '{user_query[:100]}' ---")
            retrieved_resume_context, selected_files = get_relevant_docs(
                user_query=user_query,
                user_id=user_id,
                k=k,
                vector_ids=vector_ids
            )
            retrieved_resume_context = llm.invoke(f"Summarize the following candidates data for relevance to the question keep summary for each candidate seperate but dont lose important data such as candidate information: {retrieved_resume_context}").content
        logger.debug(f"--- DEBUG: Retrieved Resume Context Length: {len(retrieved_resume_context)} ---")

    except Exception as e:
        logger.error(f"--- WARNING: Hybrid history retrieval failed: {e} ---")
        final_history_for_llm_prompt = ""
    
    

    
    # --- Step 3: Final RAG Chain for Answer Generation ---
    retriever_logic = RunnableMap({
        "context": lambda x: retrieved_resume_context, # THIS IS CRUCIAL: Pass the actual retrieved resumes here
        "history": lambda x: final_history_for_llm_prompt,  # Pass the hybrid history context
        "question": lambda x: original_user_input # Always pass the original user input as the question to LLM
    })
    
    prompt_template = PromptTemplate(
        input_variables=["context", "question", "history"],
        template="""You are an expert HR recruitment assistant. Your job is to analyze candidate resumes and answer recruiter questions accurately.

CANDIDATE DATA:
{context}

CONVERSATION HISTORY (for context and pronoun resolution):
{history}

RECRUITER QUESTION:
{question}

INSTRUCTIONS:
1. Answer ONLY based on the candidate data and conversation history provided above
2. Resolve pronouns (he/she/they/them) using the conversation history
3. Do NOT invent, assume, or hallucinate any candidate information
4. If no candidates match the criteria, clearly state that
5. Be concise and factual in your response
6. Use candidate names from the resume data
7. When comparing candidates, highlight relevant differentiators based on the question asked
8. Give answers in a structured format if multiple candidates are involved, e.g., Candidate A: ..., Candidate B: ..., etc.
9. Give answer in bullet points
10. If the question is not clear or lacks necessary information, ask for clarification instead of making assumptions
11. Try to be as detailed as possible in your answer, but do not include irrelevant information. Focus on what is being asked.
12. Use bullet points.
13. Mention candidate name first.
14. Mention relevant skills, years, companies, and frameworks.
15. If multiple candidates match, rank them by relevance.
16. If no candidate matches, say so clearly.
Your task:
- Analyze ONLY the provided candidate context.
- Never invent information.
- If information is missing, explicitly say so.
- Prefer factual extraction over interpretation.
- Keep answers concise and recruiter-friendly.
Provide a clear, direct answer:"""
    )

    rag_chain = retriever_logic | prompt_template | llm

    # Invoke the RAG chain
    logger.debug(f"--- DEBUG: Invoking RAG chain with question: '{original_user_input}' ---")

    result = rag_chain.invoke({'question': original_user_input}) 
    logger.debug(f"--- DEBUG: LLM Result Content Length: {len(result.content)} ---")
    

    # --- Add to History ---
    if result and result.content:
        history_entry = f"""User: {original_user_input}
Assistant: {result.content} 
History Document Context: {retrieved_resume_context}"""
        add_history(history_entry,hist_id,user_id,chat_group_id)
        logger.debug("--- DEBUG: History entry added. ---")
    else:
        logger.debug("--- DEBUG: No meaningful result to add to history. ---")
    
    
    return {"result":result.content, 
    "history":history_entry,
    "summarized_history": final_history_for_llm_prompt,
    "selected_files": selected_files}