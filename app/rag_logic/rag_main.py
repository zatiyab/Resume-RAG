from app.services.qdrant_client import (client,
                                        get_relevant_docs,
                                        initialize_app_data,
                                        add_vectors,
                                        add_history)
from app.crud.db_crud import get_last_history
import zipfile
from io import BytesIO
from langchain_core.runnables import RunnableMap
from langchain_core.prompts import PromptTemplate
from app.core.config import llm
# --- MAIN STREAMLIT APPLICATION LOGIC ---
def main(k, user_query,hist_id,user_id,db):
    print('\n\n\n')
    print('-'*100)
    print("--- MAIN FUNCTION STARTED ---")

    # Store the original user input (could be JD or a regular query)
    original_user_input = user_query 
    user_query = user_query.lower()

    # --- History Retrieval for LLM (for "Conversation History" in prompt) ---
    print('--- DEBUG: Retrieving Chat History ---')
    history_all_points, _ = client.scroll(
        collection_name="history",
        limit=1000, # Adjust limit as needed
        with_payload=True
    )
    
    sorted_history_points = sorted(history_all_points, key=lambda p: int(p.id), reverse=True)
    # Get last 2 history points (or more if desired for context)
    actual_last_history_items = sorted_history_points[:2] 
    selected_files = []
    # final_history_for_llm_prompt = "\n".join([p.payload['history'] for p in actual_last_history_items if 'history' in p.payload])
    history_result = get_last_history(user_id, db)

    if history_result and len(history_result) > 0:
        final_history_for_llm_prompt = history_result[0]
    else:
        final_history_for_llm_prompt = ""
    print(f"--- DEBUG: Prepared History Context Length: {len(final_history_for_llm_prompt)} ---")

    
    if ("he" in user_query.split(" ")) or ("his" in user_query.split(" ")) or ("him" in user_query.split(" ")) or ("her" in user_query.split(" ")) or ("she" in user_query.split(" ")) :
        retrieved_resume_context = ""
        try:
            history_resume_context = final_history_for_llm_prompt.split("History Document Context:")[-1]
            try:
                history_resume_context = history_resume_context.split("Resume-2")[0]
            except:
                pass
        except:
            print("History broke")
        print('No user')
    
    elif ("they" in user_query.split(" ")) or ("their" in user_query.split(" ")) or ("them" in user_query) or ("these" in user_query):
        retrieved_resume_context = ""
        try:
            history_resume_context = final_history_for_llm_prompt.split("History Document Context:")[-1]
        except:
            print("History broke")
        print('No user')
    else:
        # --- Step 2: Retrieve Relevant Resumes (for "Candidate Context" in prompt) ---
        print(f"--- DEBUG: Calling get_relevant_docs with processed query: '{user_query}' ---")
        retrieved_resume_context,selected_files = get_relevant_docs(user_query=user_query, collection='resumes', k=k)
        print(f"--- DEBUG: Retrieved Resume Context Length: {len(retrieved_resume_context)} ---")
        history_resume_context = retrieved_resume_context


    # --- Step 3: Final RAG Chain for Answer Generation ---
    retriever_logic = RunnableMap({
        "context": lambda x: retrieved_resume_context, # THIS IS CRUCIAL: Pass the actual retrieved resumes here
        "history": lambda x: final_history_for_llm_prompt, # Pass the prepared chat history here
        "question": lambda x: original_user_input # Always pass the original user input as the question to LLM
    })
    
    prompt_template = PromptTemplate(
        input_variables=["context", "question", "history"],
        template="""
You are a smart, friendly, and professional AI recruitment assistant helping HR teams and hiring managers identify top candidates based on internal resume data.

Candidate Context:
{context}

Conversation History:
{history}

Recruiter Question:
{question}

Response Instructions
✅ 1. Match Criteria Strictly

Only list candidates who meet all criteria stated in the recruiter question.

If the question requests a specific number of candidates (e.g., “5 resumes”), you must not generate placeholders or partial entries if fewer candidates match.

If there are fewer matching candidates than requested, only return the actual matches found and clearly state that fewer candidates were available.

✅ 2. No Inference or Partial Fulfillment

Do not invent or imply candidate details not explicitly provided in the Candidate Context.

Do not create entries labeled “No name specified” or “unknown candidate.”

Never attempt to partially fill a requested number of candidates.

✅ 3. Pronoun Resolution

If the question uses pronouns (e.g., he, she, they) without a named person:

Use the most recent relevant mention in the conversation history to resolve.

If uncertain, clearly state you cannot determine who is referenced.

✅ 4. Presentation

When presenting candidates, do not number beyond the actual matches.

Use a warm tone and an introduction such as:

“Here are the candidates who match your criteria:”

If no candidates match, respond politely:

“I reviewed the available resumes but could not find any candidates meeting all the specified criteria.”

✅ 5. Grounding and Evidence

For every candidate mentioned, reference only information explicitly contained in the Candidate Context.

Do not mention resumes, documents, or data sources.

🚫 Under No Circumstances:

Create or invent any candidates.

Use placeholders or partial entries to fill numeric requests.

Summarize or rephrase information in a way that introduces new facts.

Important Reminder:
If fewer candidates match than requested, provide only the exact number found. If none are found, state this clearly.
        """
    )

    rag_chain = retriever_logic | prompt_template | llm

    # Invoke the RAG chain
    print(f"--- DEBUG: Invoking RAG chain with question: '{original_user_input}' ---")

    result = rag_chain.invoke({'question': original_user_input}) 
    print(f"--- DEBUG: LLM Result Content Length: {len(result.content)} ---")
    
    # if result:
    #     st.text_area("Answer", value=result.content, height=500)
    
    # --- Resume Download Logic ---
    zip_buffer = None 
    
    if selected_files != []:
        print(f"--- DEBUG: Files selected for download: {selected_files} ---")
        import os

        folder_path = os.path.join(os.getcwd(), "resumes")
 # Verify this path is correct

        zip_buffer = BytesIO()
        with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
            for filename in selected_files:
                file_path = os.path.join(folder_path, filename)
                if os.path.exists(file_path):
                    zip_file.write(file_path, arcname=filename)
                else:
                    print(f"--- WARNING: File not found for ZIP: {file_path} ---")
        zip_buffer.seek(0)
    else:
        print("--- DEBUG: No files retrieved for download or session state empty. ---")
   
    # --- Add to History ---
    if result and result.content:
        history_entry = f"""User: {original_user_input}
Assistant: {result.content}
History Document Context: {history_resume_context}"""
        add_history(history_entry,hist_id)
        print("--- DEBUG: History entry added. ---")
    else:
        print("--- DEBUG: No meaningful result to add to history. ---")
    last_context = history_resume_context
    print("Last Context")
    
    return result.content, history_entry, zip_buffer ,selected_files