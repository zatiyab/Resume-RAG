from qdrant_client.http import models as rest
from qdrant_client.http.models import Distance, VectorParams, HnswConfigDiff  
from qdrant_client.models import PointStruct, Filter, FieldCondition, MatchValue
import pdfplumber
from app.core.config import llm
import time
from app.rag_logic.utils import basic_text_normalization
import datetime
import io
from pathlib import Path
from typing import Any
from qdrant_client import QdrantClient
from app.core.config import settings

client = None
try:
    client = QdrantClient(url=settings.QDRANT_URL, api_key=settings.QDRANT_API_KEY)
except Exception as e:
    client = None
    print(f"Warning: Qdrant client initialization failed: {e}")
import cohere
co = cohere.ClientV2()

PROJECT_ROOT = Path(__file__).resolve().parents[2]
RESUMES_DIR = PROJECT_ROOT / "resumes"
SUPPORTED_RESUME_EXTENSIONS = {".pdf", ".doc", ".docx"}


def get_resumes_dir() -> Path:
    """Return and ensure the resumes directory exists."""
    RESUMES_DIR.mkdir(parents=True, exist_ok=True)
    return RESUMES_DIR


def _embed_text(text: str, input_type: str = "search_document") -> list[float]:
    """Normalize Cohere embedding response to a single numeric vector.
    
    Args:
        text: Text to embed
        input_type: Type of input - "search_document" for resumes, "search_query" for user queries
    """
    response = co.embed(
        inputs=[{"content": [{"type": "text", "text": text}]}],
        model="embed-v4.0",
        input_type=input_type,
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

def llm_extract_metadata(resume:str,user_id,db,file_path,resume_name,vector_id):
    EXTRACTION_PROMPT = """
Extract structured info from this resume. Normalize everything strictly:
- location: city name only, Title Case (e.g. "Delhi", "Noida", "Bangalore") 
- skills: canonical names only, use these exact forms:
  JavaScript, Python, TypeScript, React, Node.js, PHP, Java, C++
  (never: JS, js, NodeJS, node, Py)

Return ONLY valid JSON, no explanation:
{{
  "name": "",
  "location": "",        
  "skills": [],          
  "experience_years": 0,
  "domain": ""           
}}

FEW SHOT EXAMPLES:
 "resume_snippet": '''
        Sneha Joshi | Pune, Maharashtra
        Exp with py, scikit, pandas, numpy, PowerBI
        Fresher — 6 months internship at Analytics Vidhya
        ''',
        "output": {{
            "name": "Sneha Joshi",
            "location": "Pune",
            "skills": ["Python", "SQL"],
            "experience_years": 0,
            "domain": "Data Science"
        }}


Resume to extract metadata from:
{resume}
""".format(resume=resume)
    try: 
        from app.schemas.resumes_schemas import MetadataResponse
        from app.crud.resume_crud import add_resume_metadata
        from app.helpers.norm_location import geocode_city
        
        structured_llm = llm.with_structured_output(MetadataResponse)
        metadata_response = structured_llm.invoke(EXTRACTION_PROMPT)
        
        metadata_content = metadata_response.model_dump() if metadata_response else "{}"
        state = geocode_city(metadata_content.get("location"))['state'] if metadata_content.get("location") else None   
        city = geocode_city(metadata_content.get("location"))['city'] if metadata_content.get("location") else None
        add_resume_metadata(user_id=user_id, file_path=file_path, resume_name=resume_name, skills=metadata_content.get("skills"), experience_years=metadata_content.get("experience_years"), raw_location=metadata_content.get("location"), state=state, city=city, domain=metadata_content.get("domain"), name=metadata_content.get("name"), resume_vector_id=vector_id, db=db)
        return metadata_content
    except Exception as e:
        print(f"Error occurred while extracting metadata: {e}")
        return {
            "name": "",
            "location": "",        
            "skills": [],          
            "experience_years": 0,
            "domain": ""           
        }

def llm_summarize_resume(resume:str):
    prompt_text = f'''You are a resume parser for a RAG (Retrieval-Augmented Generation) system.

Your job is to extract and normalize resume content into structured Markdown.
This output will be chunked and embedded — so clarity, consistency, and completeness matter more than brevity.

---

## Output Format (always use this exact structure):

### CONTACT
- Name:
- Email:
- Phone:
- Location:
- LinkedIn:
- GitHub/Portfolio:

### SUMMARY
One or two sentences capturing the candidate's profile. 

### SKILLS
Group into categories. Examples:
- **Languages:** Python, JavaScript, SQL
- **Frameworks:** React, FastAPI, LangChain
- **Tools & Platforms:** Docker, AWS, Git
- **Concepts:** Machine Learning, RAG, REST APIs

### EXPERIENCE
For each role:
**[Job Title] — [Company], [Location] | [Start Date] – [End Date or Present]**
- Bullet describing responsibility or achievement (as concise as possible)

### PROJECTS
For each project:
**[Project Name]** | [Tech stack, comma-separated]
- What it does and your role
- Link (if provided)

### EDUCATION
**[Degree], [Field] — [Institution] | [Year]**
- GPA or honors (only if mentioned)

### CERTIFICATIONS
- [Certification Name] — [Issuer] ([Year])

---

## Rules:
- Normalize synonyms: "ML" → "Machine Learning", "NLP" → "Natural Language Processing", "JS" → "JavaScript"
- Expand all abbreviations to their full form
- Preserve all dates exactly as written; do not infer or guess missing dates
- If a section is missing from the resume, write: _Not provided._
- Do not invent, infer, or hallucinate any information
- Remove filler phrases ("responsible for", "worked on", "helped with") — use action verbs
- Keep bullet points factual and scannable
- Output only the Markdown. No preamble, no explanation.
- Keep as concise as possible while following the structure and rules above.


RESUME TO PARSE:
\"\"\"
{resume}
\"\"\"
'''
    try:
        time.sleep(6.5) 
        summarized_resume = llm.invoke(prompt_text)
        summarized_resume = summarized_resume.content.strip() if summarized_resume and summarized_resume.content else ""
        sections = ["CONTACT", "SUMMARY", "SKILLS", "EXPERIENCE", "PROJECTS", "EDUCATION", "CERTIFICATIONS"]
        section_chunks = {section: summarized_resume.split(f"### {section}")[1].split('###')[0].strip() if f"### {section}" in summarized_resume else "" for section in sections}
        print(section_chunks)
    except Exception as e:
        print(f"Error occurred while summarizing resume: {e}")
        summarized_resume = "Error occurred while summarizing resume."

    return summarized_resume


def add_vectors(user_id=None, files_to_process=None,db=None):
    '''
    Reads resumes from Supabase, extracts text and generates metadata,
    then converts resumes into vectors and saves to the resume collection.
    
    Args:
        user_id: The user's ID (required)
        files_to_process: Optional list of specific file names to process.
                         If provided, skips Supabase fetch and Qdrant duplicate checks.
                         If None, fetches all files from Supabase and filters out existing vectors.
    '''
    from app.services.resumes_storage import list_user_resumes, download_resume_bytes
    
    
    print('User ID = ', user_id)
    if not user_id:
        print("No user_id provided to add_vectors. Returning.")
        return {"error": "user_id required"}
        
    
    # If specific files provided (e.g., from upload), process only those
    if files_to_process:
        resumes = files_to_process
        skipped_existing = 0
        # Still need to get current vector count for unique point IDs
        try:
            count_result = client.count(
                collection_name='resumes',
                count_filter=Filter(must=[FieldCondition(key="user_id", match=MatchValue(value=user_id))])
            )
            user_resumes_vec_cnt = count_result.count
        except Exception as e:
            print(f"Error getting vector count for user {user_id}: {e}")
            user_resumes_vec_cnt = 0
        print(f'Processing {len(resumes)} newly uploaded files for user {user_id}. Current vector count: {user_resumes_vec_cnt}')
    else:
        # Default behavior: fetch all from Supabase and check Qdrant for duplicates
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
            
        
        user_resumes_vec_cnt = len(files_vector)
        print('Last Vector Index for user ', user_id, ': ', user_resumes_vec_cnt, flush=True)
        print('Existing Vectors for user ', user_id, ': ', files_vector)

        resumes = [i for i in resumes if i not in files_vector]
        skipped_existing = total_pdf_files - len(resumes)
        print('Total No. of new resumes: ', len(resumes))
    
    points = []
    resumes_data_dict = {}
    BATCH_SIZE = 10

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
   
    batch_operations_info = []
    for resume, resume_data in resumes_data_dict.items():
        print(f'At {user_resumes_vec_cnt}/{len(resumes_data_dict)}, {resume}') 
        user_resumes_vec_cnt+=1
        resume_data= basic_text_normalization(resume_data)
        resume_data = llm_summarize_resume(resume_data)
        resume_metadata = llm_extract_metadata(resume_data, user_id=user_id, db=db, file_path=f"{user_id}/{resume}", resume_name=resume,vector_id=user_resumes_vec_cnt)
        print(f"Metadata for {resume}: {resume_metadata}")
        # Use search_document input type for resume embeddings (better for retrieval)
        vector = _embed_text(resume_data, input_type="search_document")
    
        metadata_dict = {'source': resume, 'page_content': resume_data,'user_id': user_id}  
        
        points.append(PointStruct(id=user_resumes_vec_cnt, vector=vector, payload=metadata_dict))

    if points:
        num_batches = (len(points) + BATCH_SIZE - 1) // BATCH_SIZE
        print(f"Upserting in batches of {BATCH_SIZE}. Total batches: {num_batches}")
        for batch_start in range(0, len(points), BATCH_SIZE):
            batch_points = points[batch_start:batch_start + BATCH_SIZE]
            operation_info = client.upsert(
                collection_name="resumes",
                wait=True,
                points=batch_points
            )
            print(operation_info)
            batch_operations_info.append(operation_info)

    return {
        "processed_files": len(resumes_data_dict),
        "inserted_points": len(points),
        "skipped_existing": skipped_existing,
        "operation": batch_operations_info ,
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


def get_hybrid_history(user_query: str, user_id: str, db, chat_group_id: str | None = None, k_recent: int = 2, k_similar: int = 2):
    """
    Retrieve hybrid history combining:
    1. Recent context (last K entries) for pronoun resolution
    2. Vector-similar context (semantically related past conversations)
    
    Args:
        user_query: Current user query
        user_id: User's UUID
        db: Database session (for getting recent history)
        k_recent: Number of recent history entries (default 2)
        k_similar: Number of vector-similar entries (default 2)
    
    Returns:
        Combined history string with recent and related context
    """
    from app.crud.chat_crud import get_last_k_history
    
    print(f"--- DEBUG: Building hybrid history for user {user_id}, query: '{user_query}' ---")
    
    # Step 1: Get recent history for pronoun resolution
    try:
        # Pass chat_group_id so recent history is restricted to the same chat group
        recent_histories = get_last_k_history(user_id, chat_group_id, db, k=k_recent)
        recent_text = "\n---\n".join(recent_histories)
        print(f"--- DEBUG: Retrieved {len(recent_histories)} recent history entries ---")
    except Exception as e:
        print(f"--- WARNING: Failed to get recent history: {e} ---")
        recent_text = ""
    
    # Step 2: Get vector-similar history
    similar_text = ""
    try:
        if int(k_similar) <= 0:
            print("--- DEBUG: Skipping vector-similar history retrieval because k_similar <= 0 ---")
        else:
            safe_k_similar = max(1, int(k_similar))
            query_embedding = _embed_text(user_query.lower(), input_type="search_query")

            similar_results = client.query_points(
                collection_name="history",
                query=query_embedding,
                limit=safe_k_similar,
                query_filter=Filter(
                    must=[FieldCondition(key="user_id", match=MatchValue(value=user_id))]
                ),
                score_threshold=0.4
            )

            similar_histories = [
                result.payload.get('history', '')
                for result in similar_results.points
                if result.payload
            ]

            similar_text = "\n---\n".join(similar_histories)
            print(f"--- DEBUG: Retrieved {len(similar_histories)} vector-similar history entries ---")
    except Exception as e:
        print(f"--- WARNING: Failed to get vector-similar history: {e} ---")
        similar_text = ""
    
    # Step 3: Combine with proper structure
    combined = ""
    
    if recent_text:
        combined += f"RECENT CONTEXT (for pronoun resolution):\n{recent_text}"
    
    if similar_text:
        if combined:
            combined += "\n\n"
        combined += f"RELATED CONTEXT (semantically similar conversations):\n{similar_text}"
    
    if not combined:
        print("--- DEBUG: No history found, using empty context ---")
        combined = ""
    
    print(f"--- DEBUG: Combined history length: {len(combined)} characters ---")
    return combined

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
    print(f"--- DEBUG: User ID: {user_id} ---")
    print(f"--- DEBUG: Collection: {collection} ---")

    # Check if collection exists
    if not client.collection_exists(collection):
        print(f"--- ERROR: Collection '{collection}' does not exist in Qdrant ---")
        return "", []

    # Check if there are ANY resumes for this user
    try:
        user_resumes_count = client.count(
            collection_name=collection,
            count_filter=Filter(
                must=[
                    FieldCondition(
                        key="user_id",
                        match=MatchValue(value=user_id)
                    )
                ]
            )
        )
        print(f"--- DEBUG: Total resumes for user {user_id}: {user_resumes_count.count} ---")
        if user_resumes_count.count == 0:
            print(f"--- ERROR: No resumes found in Qdrant for user {user_id}. Upload resumes first. ---")
            return "", []
    except Exception as e:
        print(f"--- ERROR: Failed to count resumes: {e} ---")

    print(f"--- DEBUG: Encoding query for retrieval: '{user_query}' ---")
    
    try:
        # Use search_query input type for better alignment with search_document embeddings
        query_embedding = _embed_text(user_query.lower(), input_type="search_query")
        print(f"--- DEBUG: Query embedding generated successfully, vector size: {len(query_embedding)} ---")
    except Exception as e:
        print(f"--- ERROR: Failed to embed query: {e} ---")
        return "", []
    
    try:
        search_result = client.query_points(
            collection_name=collection,
            query=query_embedding,
            limit=int(min(k * 2, 50)),  # Retrieve 2x K for reranking, max 50
            query_filter=Filter(
                must=[
                    FieldCondition(
                        key="user_id",
                        match=MatchValue(value=user_id)
                    )
                ]
            ),
            score_threshold=0.0  # Remove threshold initially to see all results
        )
    except Exception as e:
        print(f"--- ERROR: Qdrant query_points failed: {e} ---")
        return "", []
    
    results = search_result.model_dump()
    print(f"--- DEBUG: Qdrant Search Result (points count): {len(results['points'])} ---")
    
    if results['points']:
        for i, result in enumerate(results['points'][:3]):  # Show top 3
            print(f"--- DEBUG: Result {i+1}: ID={result['id']}, Score={result['score']:.3f}, Source={result['payload'].get('source', 'N/A')} ---")

    if not results['points']:
        print("--- WARNING: Qdrant returned 0 points. Retrieval failed. ---")
        return "", []

    # --- RERANKING STAGE: Use Cohere rerank to improve relevance ---
    print(f"--- DEBUG: Starting Cohere reranking on {len(results['points'])} candidates ---")
    
    try:
        # Prepare documents for reranking
        docs_for_rerank = [
            {
                "index": i,
                "text": result['payload'].get('page_content', '')[:1000]  # Limit to 1000 chars for rerank API
            }
            for i, result in enumerate(results['points'])
        ]
        
        rerank_result = co.rerank(
            query=user_query,
            documents=docs_for_rerank,
            model="rerank-v3.5",
            top_n=min(k, 5)  # Return at most K, but cap at 5
        )
        
        # Reorder results by rerank score
        reranked_indices = [result.index for result in rerank_result.results]
        reranked_results = [results['points'][idx] for idx in reranked_indices]
        print(f"--- DEBUG: Reranking complete. Top {len(reranked_results)} results selected ---")
    except Exception as e:
        print(f"--- WARNING: Reranking failed: {e}. Using original Qdrant order. ---")
        reranked_results = results['points'][:min(k, 5)]
    
    # --- CONTEXT COMPRESSION: Extract key fields instead of full resume ---
    all_docs_data = ''
    selected_files = []
    cnt_resume = 1
    
    for result in reranked_results:
        res_id = result['id']
        score = result['score']
        source = result['payload'].get('source', 'N/A')
        page_content = result['payload'].get('page_content', '')
        
        selected_files.append(source)
        print(f'--- DEBUG: Reranked Resume {cnt_resume}: {source}, Score: {score:.3f} ---')
        
        # Pass full resume but cap total context size
        data = f"Resume-{cnt_resume} ({source})\n\n{page_content[:2000]}"  # Limit to 2000 chars per resume
        all_docs_data += data + "\n\n---\n\n"
        cnt_resume += 1

    print(f"--- DEBUG: Total context length for LLM: {len(all_docs_data)} tokens (approx {len(all_docs_data)//4}) ---")
    print(f"--- DEBUG: Selected Files for Download: {selected_files} ---")
  
    return all_docs_data, selected_files


def initialize_app_data():
    print("--- Initializing collections and data... ---")

    if client is None:
        raise RuntimeError("Qdrant client is not initialized. Check QDRANT_URL, QDRANT_API_KEY and network connectivity.")

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
        
        client.create_payload_index(collection_name="resumes", field_name='source', field_schema=rest.PayloadSchemaType.KEYWORD)
        client.create_payload_index(collection_name="resumes", field_name='user_id', field_schema=rest.PayloadSchemaType.KEYWORD)
    
    # Initialize 'history' collection
    if not client.collection_exists("history"):
        print("--- Creating 'history' collection ---")
        client.create_collection(
            collection_name="history",
            vectors_config=VectorParams(size=1536, distance=Distance.COSINE, on_disk=False)
        )
        # Create payload index for user_id so filters/deletes by user_id are supported
        try:
            client.create_payload_index(collection_name="history", field_name="user_id", field_schema=rest.PayloadSchemaType.KEYWORD)
            print("Created payload index 'user_id' on 'history' collection")
        except Exception as e:
            print(f"Warning: failed to create payload index for history.user_id: {e}")
    print("--- Initial app data setup complete. ---")

def remove_resume_from_qdrant(user_id, file_name):
    try:
        delete_filter = Filter(
            must=[
                FieldCondition(key="user_id", match=MatchValue(value=user_id)),
                FieldCondition(key="source", match=MatchValue(value=file_name))
            ]
        )
        delete_result = client.delete(
            collection_name="resumes",
            points_selector=delete_filter
        )
        print(f"Deleted resume '{file_name}' for user '{user_id}' from Qdrant: {delete_result}")
    except Exception as e:
        print(f"Error deleting resume '{file_name}' for user '{user_id}' from Qdrant: {e}")
