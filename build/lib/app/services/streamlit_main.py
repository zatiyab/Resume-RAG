import streamlit as st
import json
import os
import zipfile
from io import BytesIO
import datetime 
from qdrant_client.http import models as rest
from qdrant_client.http.models import Distance, VectorParams, HnswConfigDiff  
from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct
from langchain_cohere import ChatCohere
from dotenv import load_dotenv
from langchain.schema.runnable import RunnableMap
from langchain.prompts import PromptTemplate
from sentence_transformers import SentenceTransformer

from data_processing import add_vectors, remove_same_files 


load_dotenv()


llm = ChatCohere(model="command-r-plus", timeout_seconds=60, cohere_api_key=os.getenv('COHERE_API_KEY'))
embedding = SentenceTransformer("BAAI/bge-large-en-v1.5")
client = QdrantClient(url="http://localhost:6333", timeout=60.0)




hist_id = 1 # Initialise history vector id
def add_history(history_text: str):
    '''
    Get history for the LLM chatbot and converts it into a vector
    and also add it to the vector history db and prints the result of the upsert operation
    '''
    global hist_id
    vector = embedding.encode(history_text)
    point = PointStruct(id=hist_id, vector=vector, payload={"created_at": datetime.datetime.utcnow().isoformat(),
                       'history':history_text})
    operation_info = client.upsert(
            collection_name="history",
            wait=True,
            points=[point]
        )
    hist_id+=1
    print(f"--- DEBUG: History Added: {operation_info} ---")


def get_relevant_docs(user_query, collection,k=5):
    '''
    Input parameters:
    user_query -> The main query that the user gives (can be a transformed JD)
    collection -> The name of the collection for which the function has to get relevant docs
    k -> Retrieving parameter how many docs to return.

    Gets relevant documents to the user query from the collection given in the input and if the
    filter data is True filters the collection accordingly and returns k documents.

    Returns all_data -> All the k documents joined together in one string
    '''

    print(f"\n--- DEBUG: Inside get_relevant_docs for query: '{user_query}' ---")

    print(f"--- DEBUG: Encoding query for retrieval: '{'Represent this sentence for retrieval: '+user_query.lower()}' ---")
    
    search_result = client.query_points(
        collection_name=collection,
        query=embedding.encode(('Represent this sentence for retrieval: ' + user_query).lower()),
        limit=k
    )
    
    results = search_result.model_dump()
    print(f"--- DEBUG: Qdrant Search Result (points count): {len(results['points'])} ---")

    all_data = ''
    selected_files = []

    if not results['points']:
        print("--- WARNING: Qdrant returned 0 points. Retrieval failed. ---")
        st.info("I couldn't find any direct matches in the resumes. Let me try a broader search.")

    cnt_resume = 1
    for result in results['points']:
        res_id = result['id']
        score = result['score']
        print(f'--- DEBUG: Retrieved ID: {res_id}, Score: {score} ---')
        print(f'--- DEBUG: Retrieved Payload Keys: {result["payload"].keys()} ---')
        source = result['payload'].get('source', 'N/A')
        page_content = result['payload'].get('page_content', '')
        print(f'--- DEBUG: Source: {source}, Page Content Length: {len(page_content)} ---')
        selected_files.append(source)
        data = f"Resume-{cnt_resume}\n\n"+page_content
        
        if data:
            all_data += str(data)
            all_data += '\n\n'
        else:
            print(f"--- WARNING: No 'page_content' found for ID {res_id} or it's empty. ---")
        cnt_resume+=1

    print(f"--- DEBUG: Total length of all_data (context to LLM): {len(all_data)} ---")
    
    if 'retrieval_result' not in st.session_state:
        st.session_state.retrieval_result = {"files": []}
    st.session_state.retrieval_result["files"] = selected_files
    print(f"--- DEBUG: Selected Files for Download (in session_state): {selected_files} ---")
  
    return all_data


def initialize_app_data():
    print("--- Initializing collections and data... ---")

    if not client.collection_exists("resumes"):
        print("--- Creating 'resumes' collection ---")
        client.create_collection(
            collection_name="resumes",
            vectors_config=VectorParams(
                size=1024,
                distance=Distance.COSINE,
                hnsw_config=HnswConfigDiff(m=16, ef_construct=128, full_scan_threshold=10000),
                on_disk=False
            )
        )
        add_vectors() 





    keyword_lst = [
    "name",
    "email",
    "phone",
    "location",
    "current_job_title",
    "current_company",
    "current_employment_location",
    "degree_major",
    "skills_total_keywords",
    "spoken_languages",
    "availability_for_joining"
    ]

    client.create_payload_index(collection_name="resumes", field_name="total_years_of_experience", field_schema=rest.PayloadSchemaType.FLOAT)
    client.create_payload_index(collection_name="resumes", field_name="graduation_year", field_schema=rest.PayloadSchemaType.INTEGER)
    for k in keyword_lst:
        client.create_payload_index(collection_name="resumes", field_name=k, field_schema=rest.PayloadSchemaType.KEYWORD)
    
    # Initialize 'history' collection
    if not client.collection_exists("history"):
        print("--- Creating 'history' collection ---")
        client.create_collection(
            collection_name="history",
            vectors_config=VectorParams(size=1024, distance=Distance.COSINE, on_disk=False)
        )
    print("--- Initial app data setup complete. ---")

if "history" not in st.session_state:
    client.delete_collection(collection_name="history")
    st.session_state['history'] = True


# Call the setup function at the top level of the script
initialize_app_data()



# --- MAIN STREAMLIT APPLICATION LOGIC ---
def main(k, user_query, is_jd_search=False):
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
    
    # final_history_for_llm_prompt = "\n".join([p.payload['history'] for p in actual_last_history_items if 'history' in p.payload])
    try:
        final_history_for_llm_prompt = actual_last_history_items[0].payload['history']
    except:
        final_history_for_llm_prompt = ""
    print(f"--- DEBUG: Prepared History Context Length: {len(final_history_for_llm_prompt)} ---")

    
    if ("he" in user_query) or ("his" in user_query) or ("him" in user_query) or ("her" in user_query) or ("she" in user_query) :
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
    
    elif ("they" in user_query) or ("their" in user_query) or ("them" in user_query) or ("these" in user_query):
        retrieved_resume_context = ""
        try:
            history_resume_context = final_history_for_llm_prompt.split("History Document Context:")[-1]
        except:
            print("History broke")
        print('No user')


    else:
    # --- Step 2: Retrieve Relevant Resumes (for "Candidate Context" in prompt) ---
        print(f"--- DEBUG: Calling get_relevant_docs with processed query: '{user_query}' ---")
        retrieved_resume_context = get_relevant_docs(user_query=user_query, collection='resumes', k=k)
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
    
    if result:
        st.text_area("Answer", value=result.content, height=500)
    
    # --- Resume Download Logic ---
    zip_buffer = None 
    if "retrieval_result" in st.session_state and st.session_state.retrieval_result["files"]:
        selected_files = st.session_state.retrieval_result["files"]
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
        add_history(history_entry)
        print("--- DEBUG: History entry added. ---")
    else:
        print("--- DEBUG: No meaningful result to add to history. ---")
    last_context = history_resume_context
    print("Last Context")
    
    return zip_buffer 