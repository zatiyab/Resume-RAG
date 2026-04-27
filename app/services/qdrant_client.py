from qdrant_client.http import models as rest
from qdrant_client.http.models import Distance, VectorParams, HnswConfigDiff  
from qdrant_client.models import PointStruct, Filter, FieldCondition, MatchValue
from app.core.config import llm
import pdfplumber
import json
import unicodedata
import time
from app.rag_logic.utils import (convert_all_docs_in_folder,
                                 basic_text_normalization,
)
import os
import datetime
import io
from pathlib import Path
from typing import Any
from qdrant_client import QdrantClient
from app.core.config import settings

client = QdrantClient(
    url=settings.QDRANT_URL, 
    api_key=settings.QDRANT_API_KEY,
)

print(client.get_collections())
import cohere
co = cohere.ClientV2()


PROJECT_ROOT = Path(__file__).resolve().parents[2]
RESUMES_DIR = PROJECT_ROOT / "resumes"
SUPPORTED_RESUME_EXTENSIONS = {".pdf", ".doc", ".docx"}


def get_resumes_dir() -> Path:
    """Return and ensure the resumes directory exists."""
    RESUMES_DIR.mkdir(parents=True, exist_ok=True)
    return RESUMES_DIR


def _embed_text(text: str) -> list[float]:
    """Normalize Cohere embedding response to a single numeric vector."""
    response = co.embed(
        inputs=[{"content": [{"type": "text", "text": text}]}],
        model="embed-v4.0",
        input_type="classification",
        embedding_types=["float"],
    )

    embeddings_obj: Any = getattr(response, "embeddings", None)
    if embeddings_obj is not None:
        for attr in ("float", "float_", "floats"):
            value = getattr(embeddings_obj, attr, None)
            if value:
                return value[0]
        if isinstance(embeddings_obj, list) and embeddings_obj:
            return embeddings_obj[0]

    if isinstance(response, dict):
        maybe_embeddings = response.get("embeddings")
        if isinstance(maybe_embeddings, list) and maybe_embeddings:
            return maybe_embeddings[0]

    raise ValueError("Could not extract float embedding from Cohere response")


def llm_create_metadata(resume:str,resume_name):
    # ... (same as your current llm_create_metadata function) ...
    prompt_text = f'''
 You are an expert resume parser.

        Your task is to extract metadata from the resume provided below and return it in the **exact JSON format** specified. The output must be a **flat JSON object** with no nested values or lists of objects. Each value must be a simple string. If any field is not available, leave it as an empty string `""` (do not remove the key).

        💡 Output Requirements:
        - Output must be valid JSON only — no preamble, no explanation.
        - All values must be strings (even for numbers, dates, booleans).
        - Include appropriate content type in each value (e.g., phone, email, numeric string, year).
        - Concatenate items as comma-separated strings where appropriate.
        - Give no explanations

        💼 Resume to parse:
        \"\"\"
        {resume}
        \"\"\"

        🎯 Target JSON structure (with field descriptions and type hints):
        {{
        "name": "Full name of the candidate (string)",
        "email": "Primary email address (string)",
        "phone": "Phone number with or without country code (string)",
        "location": "Current Location give only state and country (string)",        

        "total_years_of_experience": "(Mandatory-Give the resume some value for this key always)Total professional experience in years (string of float e.g., '5.6')",
        "current_job_title": "Most recent job title (string)",
        "current_company": "Most recent company name (string)",
        "current_employment_location": "Location of the current job (string)",        


        "degree_major": "Major/field of study (string)",

       
        "skills_total_keywords": "Union of all skills-apis,frameworks,databases,languages,cloud-hosting,devtools,no job positions,other non cs skills too(flat comma-separated string)",

        "spoken_languages": "Fluent or proficient languages (comma-separated string)",

        "availability_for_joining": "Availability to join (e.g., 'Immediate', '1 Month') (string)",
        
        }}
        '''
    try:
        # Generates metadata/payload for the given resume
        

        # Add a delay between calls
        time.sleep(6.5)  # 60 seconds / 10 calls = 6 seconds per call

        metadata_result = llm.invoke(prompt_text)
        print("Here is metadata result")
        print(metadata_result)
        try:
            data = metadata_result.content.strip('```')
            data = data.lstrip('json')
            metadata_dict = json.loads(data)
            print()
            print(data)
            print('-'*50)
            print(metadata_dict)
        except:
            print('Data Loading Problem')
            print(data)
            metadata_dict = {'source':resume_name}
            
   
        return metadata_dict
    except Exception as e:
        print(e,flush=True)
        print('LLM problem')
        print(prompt_text)
        return {'source':resume_name}


def add_vectors(resumes_folder: str | Path | None = None, user_id=None):
    '''
    Reads all the resumes securely from Supabase extracts text and calls function to generate metadata 
    then converts the resume into a vector and save it into the resume collection along with their respective metadatas.
    '''
    print('User ID = ', user_id)
    if not user_id:
        print("No user_id provided to add_vectors. Returning.")
        return {"error": "user_id required"}
        
    from app.services.resumes_storage import list_user_resumes, download_resume_bytes
    
    try:
        supabase_files = list_user_resumes(user_id)
        if not isinstance(supabase_files, list):
            supabase_files = []
    except Exception as e:
        print(f"Error fetching from Supabase: {e}")
        supabase_files = []

    resumes = [f["name"] for f in supabase_files if f.get("name") and f["name"].lower().endswith(".pdf")]
    total_pdf_files = len(resumes)
    
    # Try filtering Qdrant for this user to avoid redundant processing
    try:
        all_vec_user = client.scroll(
            collection_name='resumes',
            scroll_filter=Filter(must=[FieldCondition(key="user_id", match=MatchValue(value=user_id))]),
            with_payload=['source'],
            limit=1000000
        )
        files_vector = [i.payload['source'] for i in all_vec_user[0]] if all_vec_user and all_vec_user[0] else []
    except Exception as e:
        print(f"Error checking existing vectors in Qdrant: {e}")
        files_vector = []
        
    try:
        all_vec_global = client.scroll(collection_name='resumes', with_payload=False, limit=1000000)
        last_indx = max([x.id for x in all_vec_global[0]]) if all_vec_global and all_vec_global[0] else 0
    except:
        last_indx = 0

    print('Last Vector Index Globally: ', last_indx, flush=True)
    print('Existing Vectors for user: ', files_vector)
    
    resumes = [i for i in resumes if i not in files_vector]
    skipped_existing = total_pdf_files - len(resumes)
    print('Total No. of new resumes: ', len(resumes))
    
    points = []
    resumes_data_dict = {}
    
    for resume in resumes:
        resume_data = ''
        file_path = f"{user_id}/{resume}"
        try:
            pdf_bytes = download_resume_bytes(file_path)
            with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
                for i, page in enumerate(pdf.pages):
                    text = page.extract_text()
                    if text:
                        resume_data += text.strip()
                    else:
                        print(f"No text found on page {i}.")

                    tables = page.extract_tables()
                    if tables:
                        tables_data = ''
                        for table in tables:
                            table_str = "\n".join([" | ".join([str(cell) if cell is not None else "" for cell in row]) for row in table])
                            tables_data += ('\n' + table_str)
                        resume_data += tables_data
                        
            if resume_data not in resumes_data_dict.values():
                resumes_data_dict[resume] = resume_data
        except Exception as e:
            print(f"Failed to process {resume} from Supabase: {e}")
    
    for resume, resume_data in resumes_data_dict.items():
        last_indx+=1
        resume_data= basic_text_normalization(resume_data)
        metadata_dict = llm_create_metadata(resume_data.lower(),resume_name=resume)
        vector = _embed_text(resume_data.lower())
    
        list_fields =[
            "skills_languages",
            "skills_frameworks",
            "skills_databases",
            "skills_devtools",
            "skills_apis",
            "skills_other",
            "skills_total_keywords",
            "project_titles",
            "project_domains",
            "project_roles",
            "project_technologies_used",
            "spoken_languages",
            "interests_or_hobbies"
        ]

        for k,v in metadata_dict.items():
            if k == 'total_years_of_experience' and (v != "" and v != " "): # Changed condition to check for non-empty string
                try:
                    metadata_dict[k] =float(v)
                except ValueError: # Catch specific error for float conversion
                    metadata_dict[k] ='' # Set to empty string on failure
            if k == 'graduation_year' and (v != "" and v != " "): # Changed condition
                try:
                    metadata_dict[k] = int(v)
                except ValueError: # Catch specific error for int conversion
                    metadata_dict[k] = "" # Set to empty string on failure
            

            # Normalizing case for string values in metadata_dict for consistency
            if isinstance(v, str):
                metadata_dict[k] = v.lower()
        
        for k,v in metadata_dict.items():
            if k in list_fields and isinstance(v, str): # Only split if it's a string
                metadata_dict[k] = [i.strip() for i in v.split(',') if i.strip()] # Split by comma and strip whitespace
        
        metadata_dict['source'] = resume
        metadata_dict['page_content'] = resume_data
        metadata_dict['user_id'] = user_id
        
        points.append(PointStruct(id=last_indx, vector=vector, payload=metadata_dict))
        print(f'At {last_indx}/{len(resumes_data_dict)}, {resume}') # Use len(resumes_data_dict) for total unique resumes processed
    operation_info = None
    if points: # Check if points list is not empty
        operation_info = client.upsert(
                collection_name="resumes",
                wait=True,
                points=points
            )
        print(operation_info)
    return {
        "processed_files": len(resumes_data_dict),
        "inserted_points": len(points),
        "skipped_existing": skipped_existing,
        "operation": str(operation_info) if operation_info else None,
    }
    

def add_history(history_text: str, hist_id, user_id):
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
                       'user_id':user_id})
    operation_info = client.upsert(
            collection_name="history",
            wait=True,
            points=[point]
        )

    print(f"--- DEBUG: History Added: {operation_info} ---")



def get_relevant_docs(user_query,user_id,collection,k=5):
    '''
    Input parameters:
    user_query -> The main query that the user gives (can be a transformed JD)
    collection -> The name of the collection for which the function has to get relevant docs
    k -> Retrieving parameter how many docs to return.

    Gets relevant documents to the user query from the collection given in the input and if the
    
    Returns all_docs_data -> All the k documents joined together in one string
    '''

    print(f"\n--- DEBUG: Inside get_relevant_docs for query: '{user_query}' ---")

    print(f"--- DEBUG: Encoding query for retrieval: '{'Represent this sentence for retrieval: '+user_query.lower()}' ---")
    
    search_result = client.query_points(
        collection_name=collection,
        query=_embed_text('Represent this sentence for retrieval: '+user_query.lower()),
        limit=int(k),
        query_filter=Filter(
            must=[
                FieldCondition(
                    key="user_id",
                    match=MatchValue(value=user_id)
                )
            ]
        )
    )
    
    results = search_result.model_dump()
    print(f"--- DEBUG: Qdrant Search Result (points count): {len(results['points'])} ---")

    all_docs_data = ''
    selected_files = []

    if not results['points']:
        print("--- WARNING: Qdrant returned 0 points. Retrieval failed. ---")
        
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
            all_docs_data += str(data)
            all_docs_data += '\n\n'
        else:
            print(f"--- WARNING: No 'page_content' found for ID {res_id} or it's empty. ---")
        cnt_resume+=1

    print(f"--- DEBUG: Total length of all_docs_data (context to LLM): {len(all_docs_data)} ---")
    
    
    print(f"--- DEBUG: Selected Files for Download (in session_state): {selected_files} ---")
  
    return all_docs_data,selected_files


def initialize_app_data(user_id):
    print("--- Initializing collections and data... ---")

    if not client.collection_exists("resumes"):
        print("--- Creating 'resumes' collection ---")
        client.create_collection(
            collection_name="resumes",
            vectors_config=VectorParams(
                size=1536,
                distance=Distance.COSINE,
                hnsw_config=HnswConfigDiff(m=16, ef_construct=128, full_scan_threshold=10000),
                on_disk=False
            )
        )
        add_vectors(user_id=user_id) 

        keyword_lst = ["user_id", "name", "email", "phone", "location", "current_job_title", "current_company", "current_employment_location", "degree_major", "skills_total_keywords", "spoken_languages", "availability_for_joining"]

        client.create_payload_index(collection_name="resumes", field_name="total_years_of_experience", field_schema=rest.PayloadSchemaType.FLOAT)
        client.create_payload_index(collection_name="resumes", field_name="graduation_year", field_schema=rest.PayloadSchemaType.INTEGER)
        for k in keyword_lst:
            client.create_payload_index(collection_name="resumes", field_name=k, field_schema=rest.PayloadSchemaType.KEYWORD)
    
    # Initialize 'history' collection
    if not client.collection_exists("history"):
        print("--- Creating 'history' collection ---")
        client.create_collection(
            collection_name="history",
            vectors_config=VectorParams(size=1536, distance=Distance.COSINE, on_disk=False)
        )
    print("--- Initial app data setup complete. ---")


