# backend/server.py
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import os
import json
import zipfile
from io import BytesIO
import datetime

# --- Import your existing core logic functions ---
# Make sure these paths are correct relative to server.py
from data_processing import add_vectors, clean_data, remove_same_files, basic_text_normalization, llm_create_metadata, process_data
from metadata_filter import generate_filter
from convert_to_pdf import create_unique, convert_all_docs_in_folder # Assuming convert_all_docs_in_folder is also used somewhere if needed

# --- Qdrant and LLM Initializations (from your streamlit_main.py) ---
from qdrant_client.http import models as rest
from qdrant_client.http.models import Distance, VectorParams, HnswConfigDiff
from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct
from langchain_cohere import ChatCohere
from langchain.prompts import PromptTemplate
from langchain.schema.runnable import RunnableMap
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv

load_dotenv() # Load environment variables from .env

app = Flask(__name__)
CORS(app) # Enable CORS for all routes, allowing React frontend to connect

# --- Global Initializations (Run once when Flask app starts) ---
llm = ChatCohere(model="command-r-plus", timeout_seconds=60, cohere_api_key=os.getenv('COHERE_API_KEY'))
embedding = SentenceTransformer("BAAI/bge-large-en-v1.5")
client = QdrantClient(url="http://localhost:6333", timeout=60.0)

# Global variable for unique metadata values
all_dict = {}

# --- Helper Functions (Copied from your streamlit_main.py and data_processing.py) ---
# These are needed for the backend logic and should be consistent with your original files.
# If these functions are fully defined in data_processing.py, you can remove these definitions
# and just rely on imports. I'm putting them here for a self-contained server example.

hist_id = 1
def add_history(history_text: str):
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

def get_relevant_docs(user_query, collection, filter_data=True, k=5):
    global all_dict # Access the global all_dict here

    print(f"\n--- DEBUG: Inside get_relevant_docs for query: '{user_query}' ---")

    if filter_data:
        filter_payload = {}#generate_filter(all_dict=all_dict, user_query=user_query)
        actual_filter = filter_payload if isinstance(filter_payload, dict) else {}
        
        print(f"--- DEBUG: Filter Generated: {filter_payload} (Type: {type(filter_payload)}) ---")
        print(f"--- DEBUG: Actual Filter used for Qdrant: {actual_filter} ---")
        if isinstance(filter_payload, str):
            print(f"--- WARNING: Filter generation returned a string: '{filter_payload}'. Applying no filter. ---")
            actual_filter = {}
    else:
        actual_filter = {}
        print("--- DEBUG: Filter data is False, no filter applied. ---")

    print(f"--- DEBUG: Encoding query for retrieval: '{'Represent this sentence for retrieval: '+user_query.lower()}' ---")
    
    search_result = client.query_points(
        collection_name=collection,
        query=embedding.encode(('Represent this sentence for retrieval: ' + user_query).lower()),
        limit=k,
        query_filter=actual_filter
    )
    
    results = search_result.model_dump()
    print(f"--- DEBUG: Qdrant Search Result (points count): {len(results['points'])} ---")

    all_data = ''
    selected_files = []

    if not results['points']:
        print("--- WARNING: Qdrant returned 0 points. Retrieval failed. ---")
        if filter_data and actual_filter:
            print("--- DEBUG: Retrying search without filters. ---")
            search_result_no_filter = client.query_points(
                collection_name=collection,
                query=embedding.encode(('Represent this sentence for retrieval: ' + user_query).lower()),
                limit=k,
                query_filter={}
            )
            results_no_filter = search_result_no_filter.model_dump()
            if results_no_filter['points']:
                print("--- DEBUG: Found results without filters. Using these. ---")
                results = results_no_filter
            else:
                return "", [] # Return empty context and empty files
        else:
            return "", [] # Return empty context and empty files

    for result in results['points']:
        res_id = result['id']
        score = result['score']
        print(f'--- DEBUG: Retrieved ID: {res_id}, Score: {score} ---')
        print(f'--- DEBUG: Retrieved Payload Keys: {result["payload"].keys()} ---')
        
        source = result['payload'].get('source', 'N/A')
        page_content = result['payload'].get('page_content', '')
        print(f'--- DEBUG: Source: {source}, Page Content Length: {len(page_content)} ---')
        selected_files.append(source)
        data = page_content

        if data:
            all_data += str(data)
            all_data += '\n\n'
        else:
            print(f"--- WARNING: No 'page_content' found for ID {res_id} or it's empty. ---")

    print(f"--- DEBUG: Total length of all_data (context to LLM): {len(all_data)} ---")
    
    return all_data, selected_files


# --- APP STARTUP SETUP (Runs once when Flask app starts) ---
def initialize_app_data():
    global all_dict
    print("--- Initializing collections and data... ---")
    
    # Ensure 'resumes' directory exists
    if not os.path.exists('resumes'):
        os.makedirs('resumes')

    # Initialize 'resumes' collection
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
        # add_vectors() # This would process existing resumes on startup.
                       # For a web app, we'll trigger this via /upload endpoint.
    
    # Load and clean unique.json for payload indexing
    try:
        with open('unique.json','r') as f:
            all_dict = json.load(f)
            all_dict = clean_data(all_dict)
    except FileNotFoundError:
        print("--- WARNING: unique.json not found. It will be created upon first resume processing. ---")
        all_dict = {} # Initialize empty if not found

    # Re-create/update unique.json based on current Qdrant data and ensure payload indexes
    # This part can be moved to add_vectors if you want it to happen only when new resumes are added.
    # For simplicity, keeping it here to ensure indexes are always there.
    if all_dict: # Only proceed if all_dict has some content
        print("--- Updating unique.json and setting payload indexes ---")
        with open("unique.json", "w", encoding="utf-8") as f:  
            all_dict = create_unique(client, all_dict) # This modifies all_dict
            all_dict = clean_data(all_dict) # Clean after create_unique as well
            json.dump(all_dict, f, ensure_ascii=False, indent=4)

        for k in all_dict.keys():
            try: # Use try-except to handle cases where index might already exist
                if k == 'total_years_of_experience':
                    client.create_payload_index(collection_name="resumes", field_name=k, field_schema=rest.PayloadSchemaType.FLOAT)
                elif k == 'graduation_year':
                    client.create_payload_index(collection_name="resumes", field_name=k, field_schema=rest.PayloadSchemaType.INTEGER)
                else:
                    client.create_payload_index(collection_name="resumes", field_name=k, field_schema=rest.PayloadSchemaType.KEYWORD)
            except Exception as e:
                print(f"--- WARNING: Could not create payload index for {k}: {e} ---")
    else:
        print("--- INFO: unique.json is empty, skipping payload index creation. ---")

    # Initialize 'history' collection
    if not client.collection_exists("history"):
        print("--- Creating 'history' collection ---")
        client.create_collection(
            collection_name="history",
            vectors_config=VectorParams(size=1024, distance=Distance.COSINE, on_disk=False)
        )
    print("--- Initial app data setup complete. ---")

# Call the setup function when the Flask app starts
with app.app_context():
    initialize_app_data()


# --- API ENDPOINTS ---

@app.route('/upload_resumes', methods=['POST'])
def upload_resumes():
    if 'files' not in request.files:
        return jsonify({"error": "No file part"}), 400
    
    uploaded_files = request.files.getlist('files')
    if not uploaded_files:
        return jsonify({"error": "No selected file"}), 400

    resume_dir = 'resumes'
    if not os.path.exists(resume_dir):
        os.makedirs(resume_dir)

    for uploaded_file in uploaded_files:
        if uploaded_file.filename == '':
            continue
        filepath = os.path.join(resume_dir, uploaded_file.filename)
        uploaded_file.save(filepath)
        print(f"--- DEBUG: Saved {uploaded_file.filename} to {filepath} ---")
    
    try:
        # This will process newly uploaded files and add vectors
        add_vectors() # This function needs to be robust enough to handle new files only
                      # Your add_vectors already checks for existing files.
        # After adding vectors, unique.json and indexes might need update
        global all_dict
        with open('unique.json','r') as f:
            all_dict = json.load(f)
            all_dict = clean_data(all_dict)
        # Re-create payload indexes if new types of metadata appear
        for k in all_dict.keys():
            try:
                if k == 'total_years_of_experience':
                    client.create_payload_index(collection_name="resumes", field_name=k, field_schema=rest.PayloadSchemaType.FLOAT)
                elif k == 'graduation_year':
                    client.create_payload_index(collection_name="resumes", field_name=k, field_schema=rest.PayloadSchemaType.INTEGER)
                else:
                    client.create_payload_index(collection_name="resumes", field_name=k, field_schema=rest.PayloadSchemaType.KEYWORD)
            except Exception as e:
                # This might fail if index already exists, which is fine.
                print(f"--- WARNING: Could not create payload index for {k} during upload: {e} ---")

        return jsonify({"message": f"Successfully uploaded and processed {len(uploaded_files)} resumes."}), 200
    except Exception as e:
        print(f"--- ERROR: During resume processing: {e} ---")
        return jsonify({"error": f"Failed to process resumes: {str(e)}"}), 500


@app.route('/search', methods=['POST'])
def search_resumes():
    data = request.get_json()
    user_input = data.get('query', '').lower()
    k = int(data.get('k', 5))
    is_jd_search = data.get('is_jd_search', False)

    if not user_input:
        return jsonify({"error": "Query cannot be empty"}), 400

    original_user_input = user_input

    # --- Step 1: JD to Search Query Conversion (if it's a JD search) ---
    if is_jd_search:
        print("--- DEBUG: Performing JD to Query Conversion ---")
        jd_to_query_prompt = PromptTemplate(
            input_variables=["job_description"],
            template="""You are an expert recruitment assistant. Your task is to analyze the provided Job Description and generate a highly effective search query to find the most relevant resumes from a database.
            Focus on extracting:
            - **Key Skills:** (e.g., "Python, Machine Learning, TensorFlow, AWS")
            - **Experience Level:** (e.g., "5+ years of experience", "junior", "senior")
            - **Role/Title:** (e.g., "Data Scientist", "Full Stack Developer")
            - **Key Responsibilities/Keywords:** (e.g., "building scalable APIs", "NLP models", "data pipelines")

            Combine these into a concise, actionable search query. Do NOT include any conversational text, just the query.

            Job Description:
            {job_description}

            Resume Search Query:
            """
        )
        jd_query_generator_chain = jd_to_query_prompt | llm
        
        try:
            generated_query_result = jd_query_generator_chain.invoke({'job_description': original_user_input})
            user_input = generated_query_result.content # Update user_input with the generated query
            print(f"--- DEBUG: Generated Search Query from JD: {user_input} ---")
        except Exception as e:
            print(f"--- ERROR: Failed to generate query from JD: {e} ---")
            return jsonify({"error": f"Failed to process JD: {str(e)}"}), 500
    
    # --- History Retrieval for LLM ---
    print('--- DEBUG: Retrieving Chat History for LLM Context ---')
    history_all_points, _ = client.scroll(
        collection_name="history",
        limit=1000,
        with_payload=True
    )
    sorted_history_points = sorted(history_all_points, key=lambda p: int(p.id), reverse=True)
    actual_last_history_items = sorted_history_points[:2] 
    final_history_for_llm_prompt = "\n".join([p.payload['history'] for p in actual_last_history_items if 'history' in p.payload])
    print(f"--- DEBUG: Prepared History Context Length: {len(final_history_for_llm_prompt)} ---")


    # --- Step 2: Retrieve Relevant Resumes ---
    print(f"--- DEBUG: Calling get_relevant_docs with processed query: '{user_input}' ---")
    retrieved_resume_context, selected_files = get_relevant_docs(user_query=user_input, collection='resumes', filter_data=True, k=k)
    print(f"--- DEBUG: Retrieved Resume Context Length: {len(retrieved_resume_context)} ---")
    print(f"--- DEBUG: Files selected for download: {selected_files} ---")

    # --- Step 3: Final RAG Chain for Answer Generation ---
    retriever_logic = RunnableMap({
        "context": lambda x: retrieved_resume_context,
        "history": lambda x: final_history_for_llm_prompt,
        "question": lambda x: original_user_input # Always pass the original user input as the question
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

If there are fewer matching candidates than requested, only return the actual matches found and clearly state that fewer candidates are available.

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

    try:
        result = rag_chain.invoke({'question': original_user_input})
        answer_content = result.content
        print(f"--- DEBUG: LLM Result Content Length: {len(answer_content)} ---")
    except Exception as e:
        print(f"--- ERROR: During LLM invocation: {e} ---")
        answer_content = "I'm sorry, I encountered an error while generating the response."

    # --- Add to History ---
    if answer_content and answer_content != "I'm sorry, I encountered an error while generating the response.":
        history_entry = f"""User: {original_user_input}
Assistant: {answer_content}"""
        add_history(history_entry)
        print("--- DEBUG: History entry added. ---")
    else:
        print("--- DEBUG: No meaningful result to add to history. ---")
    
    return jsonify({"answer": answer_content, "selected_files": selected_files}), 200


@app.route('/download_resumes', methods=['POST'])
def download_resumes():
    data = request.get_json()
    selected_files = data.get('files', [])

    if not selected_files:
        return jsonify({"error": "No files specified for download"}), 400

    folder_path = "resumes" # Assuming resumes folder is in the same directory as server.py
    zip_buffer = BytesIO()

    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
        for filename in selected_files:
            file_path = os.path.join(folder_path, filename)
            if os.path.exists(file_path):
                zip_file.write(file_path, arcname=filename)
            else:
                print(f"--- WARNING: File not found for ZIP: {file_path} ---")
    zip_buffer.seek(0)

    return send_file(
        zip_buffer,
        mimetype='application/zip',
        as_attachment=True,
        download_name='selected_resumes.zip'
    ), 200


if __name__ == '__main__':
    # Ensure the resumes directory exists before starting
    if not os.path.exists('resumes'):
        os.makedirs('resumes')
    app.run(debug=True, port=5000) # Run on port 5000