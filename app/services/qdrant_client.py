from qdrant_client.http import models as rest
from app.core.logger import logger
from qdrant_client.http.models import Distance, VectorParams, HnswConfigDiff  
from qdrant_client.models import HasIdCondition, Filter
import pdfplumber
import time
from app.crud.resume_crud import find_resume_id_for_duplicate
from app.rag_logic.utils import basic_text_normalization
import io
from pathlib import Path
from typing import Any
import uuid
from app.clients import (get_qdrant, get_co,get_llm)

co = get_co()
qdrant_client = get_qdrant()
llm = get_llm()
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

def llm_extract_metadata(resume:str,db,file_path,resume_name,vector_id):
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
        from app.crud.resume_crud import add_resume
        from app.helpers.norm_location import geocode_city
        
        structured_llm = llm.with_structured_output(MetadataResponse)
        metadata_response = structured_llm.invoke(EXTRACTION_PROMPT)
        
        metadata_content = metadata_response.model_dump() if metadata_response else "{}"
        
    except Exception as e:
        logger.error(f"Error occurred while extracting metadata: {e}")
        metadata_content = {
            "name": "",
            "location": "",        
            "skills": [],          
            "experience_years": 0,
            "domain": ""           
        }
        
    
    state = geocode_city(metadata_content.get("location"))['state'] if metadata_content.get("location") else "Unknown"   
    city = geocode_city(metadata_content.get("location"))['city'] if metadata_content.get("location") else "Unknown"
    
    add_resume(file_path=file_path, 
                resume_name=resume_name, 
                skills=metadata_content.get("skills"), 
                experience_years=metadata_content.get("experience_years"), 
                raw_location=metadata_content.get("location"), 
                state=state, 
                city=city, 
                domain=metadata_content.get("domain"), 
                name=metadata_content.get("name"), 
                resume_vector_id=vector_id, 
                db=db)

    return metadata_content

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
        logger.info(section_chunks)
    except Exception as e:
        logger.error(f"Error occurred while summarizing resume: {e}")
        summarized_resume = "Error occurred while summarizing resume."

    return summarized_resume


def add_vectors(user_id=None, files_to_process:list=[],db=None, duplicate_files:list = []) -> dict:
    '''
    Reads resumes from Supabase, extracts text and generates metadata,
    then converts resumes into vectors and saves to the resume collection.
    
    Args:
        user_id: The user's ID (required)
        files_to_process: Optional list of specific file names to process.
                         If provided, skips Supabase fetch and Qdrant duplicate checks.
                         If None, fetches all files from Supabase and filters out existing vectors.
        duplicate_files: List of file names that are duplicates and should be skipped.
    '''
    from app.services.resumes_storage import download_resume_bytes
    from app.crud.resume_crud import get_cnt_resumes,list_resumes
    from app.vector_crud.resumes_crud import batch_add_resumes as batch_add_resumes_to_qdrant
    from app.crud.user_resumes_crud import add_user_resumes,duplicate_resume_check
    from app.crud.resume_crud import get_resume_id_by_vector_id
    logger.info('User ID : ', user_id)
    
    resumes_in_db_qdrant = [resume.resume_name for resume in list_resumes(db)]
    resume_vector_id = get_cnt_resumes(db)  # Start vector IDs from the current count of resumes in DB to avoid collisions
    logger.info('Last Vector Id for user ', user_id, ': ', resume_vector_id)
    logger.info('Existing Vectors for user ', user_id, ': ', resumes_in_db_qdrant)

    logger.info('Total No. of new resumes: ', len(files_to_process))
    logger.info('Duplicate files to skip: ', duplicate_files)
    logger.info('Files to process(not duplicates): ', files_to_process)

    user_uuid = uuid.UUID(user_id) if isinstance(user_id, str) else user_id

    points = []
    resumes_data_dict = {}

    
    for duplicate in duplicate_files:
        if duplicate_resume_check(duplicate,user_id, db):
            logger.info(f"Duplicate file '{duplicate}' not found in DB during duplicate check. This should not happen. Skipping.")
            continue
        resume_id = find_resume_id_for_duplicate(duplicate, db) 
        if resume_id is None:
            logger.info(f"Could not find resume_id for duplicate file: {duplicate}")
            continue
        logger.info(f"Skipping duplicate file from processing: {duplicate}")
        resume_uuid = uuid.UUID(str(resume_id))
        add_user_resumes(user_id=user_uuid, resume_id=resume_uuid, db=db)
        
    
    for resume in files_to_process:
        resume_data = ''
        file_path = resume
        try:
            pdf_bytes = download_resume_bytes(file_path)
            with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
                for i, page in enumerate(pdf.pages):
                    text = page.extract_text()
                    if text:
                        resume_data += text.strip()
                    else:
                        logger.info(f"No text found on page {i}.")

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
            logger.error(f"Failed to process {resume} from Supabase: {e}")
   

    resume_vector_ids = []
    
    for resume, resume_data in resumes_data_dict.items():
        logger.info(f'At {resume_vector_id}/{len(resumes_data_dict)}, {resume}') 
        

        resume_data= basic_text_normalization(resume_data)
        resume_data = llm_summarize_resume(resume_data)
        resume_metadata = llm_extract_metadata(resume_data, 
                                               db=db, 
                                               file_path=resume, 
                                               resume_name=resume,
                                               vector_id=resume_vector_id)
        
        try:
            resume_id = get_resume_id_by_vector_id(resume_vector_id, db)
        except Exception as e:
            logger.error(f"Error occurred while fetching resume ID for vector ID {resume_vector_id}: {e}")
            continue
        add_user_resumes(user_id=user_uuid, resume_id=uuid.UUID(str(resume_id)), db=db)
    

        logger.info(f"Metadata for {resume}: {resume_metadata}")
        
        resume_vector_ids.append(resume_vector_id)
        resume_vector_id+=1
        
    
    batch_operations_info = batch_add_resumes_to_qdrant(
        resume_names=list(resumes_data_dict.keys()),
        resume_texts=list(resumes_data_dict.values()),
        resume_vector_ids=resume_vector_ids,
        )

    return {
        "processed_files": len(resumes_data_dict),
        "inserted_points": len(points),
        "duplicate_files": duplicate_files,
        "operation": batch_operations_info ,
    }





def get_hybrid_history(
    user_query: str,
    user_id: str,
    db,
    chat_group_id: str | None = None,
    k_recent: int = 2,
    k_similar: int = 2,
    use_vector_similarity: bool = False,
):
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
    from app.vector_crud.history_crud import get_similar_history
    
    logger.debug(f"--- DEBUG: Building hybrid history for user {user_id}, query: '{user_query}' ---")
    
    # Step 1: Get recent history for pronoun resolution
    try:
        # Pass chat_group_id so recent history is restricted to the same chat group
        recent_histories = get_last_k_history(user_id, chat_group_id, db, k=k_recent)
        recent_text = "\n---\n".join(recent_histories)

        logger.debug(f"--- DEBUG: Retrieved {len(recent_histories)} recent history entries ---")
    except Exception as e:
        logger.error(f"--- WARNING: Failed to get recent history: {e} ---")
        recent_text = ""
    
    # Step 2: Get vector-similar history
    # This is opt-in because semantic lookup can be slow enough to hurt page reads.
    similar_text = ""
    try:
        if not use_vector_similarity or int(k_similar) <= 0:
            logger.debug("--- DEBUG: Skipping vector-similar history retrieval because k_similar <= 0 ---")
        else:
            safe_k_similar = max(1, int(k_similar))
            similar_histories = get_similar_history(user_id, chat_group_id, user_query, k=safe_k_similar)
            similar_text = "\n---\n".join(similar_histories)
            logger.debug(f"--- DEBUG: Retrieved {len(similar_histories)} vector-similar history entries ---")
    except Exception as e:
        logger.error(f"--- WARNING: Failed to get vector-similar history: {e} ---")
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
        logger.debug("--- DEBUG: No history found, using empty context ---")
        combined = ""
    
    logger.debug(f"--- DEBUG: Combined history length: {len(combined)} characters ---")
    return combined

def get_relevant_docs(user_query,user_id,k=5,vector_ids=[]):
    '''
    Input parameters:
    user_query -> The main query that the user gives (can be a transformed JD)
    collection -> The name of the collection for which the function has to get relevant docs
    k -> Retrieving parameter how many docs to return.

    Gets relevant documents to the user query from the collection given in the input and if the
    
    Returns all_docs_data -> All the k documents joined together in one string
    '''

    logger.debug(f"\n--- DEBUG: Inside get_relevant_docs for query: '{user_query}' ---")
    logger.debug(f"--- DEBUG: User ID: {user_id} ---")

    # Check if collection exists
    if not qdrant_client.collection_exists("resumes"):
        logger.error(f"--- ERROR: Collection 'resumes' does not exist in Qdrant ---")
        return "", []

    # Check if there are ANY resumes for this user
    must_conditions = []
    if vector_ids:
        must_conditions.append(HasIdCondition(has_id=vector_ids))

    try:
        user_resumes_count = qdrant_client.count(
            collection_name="resumes",
            count_filter=Filter(
                must=must_conditions
            )
        )

        logger.debug(f"--- DEBUG: Total resumes for user {user_id}: {user_resumes_count.count} ---")
        if user_resumes_count.count == 0:
            logger.error(f"--- ERROR: No resumes found in Qdrant for user {user_id}. Upload resumes first. ---")
            return "", []
    except Exception as e:
        logger.error(f"--- ERROR: Failed to count resumes: {e} ---")

    logger.debug(f"--- DEBUG: Encoding query for retrieval: '{user_query}' ---")
    
    
    
    try:
        from app.vector_crud.resumes_crud import get_similar_resumes
        similar_resumes = get_similar_resumes(user_query, user_id, must_conditions, k=k)
    except Exception as e:
        logger.error(f"--- ERROR: Qdrant query_points failed: {e} ---")
        return "", []

    # Normalize retrieval result to a dict with a `points` list.
    if hasattr(similar_resumes, "model_dump"):
        results = similar_resumes.model_dump()
    elif hasattr(similar_resumes, "points"):
        results = {
            "points": [
                {
                    "id": point.id,
                    "score": getattr(point, "score", 0.0),
                    "payload": point.payload or {},
                }
                for point in (similar_resumes.points or [])
            ]
        }
    elif isinstance(similar_resumes, list):
        results = {"points": similar_resumes}
    else:
        results = {"points": []}

    logger.debug(f"--- DEBUG: Retrieved {len(results['points'])} similar resumes from Qdrant ---")
    logger.debug(f"--- DEBUG: Qdrant Search Result (points count): {len(results['points'])} ---")
    
    if results['points']:
        for i, result in enumerate(results['points'][:3]):  # Show top 3
            logger.debug(f"--- DEBUG: Result {i+1}: ID={result['id']}, Score={result['score']:.3f}, Source={result['payload'].get('source', 'N/A')} ---")

    if not results['points']:
        logger.error("--- WARNING: Qdrant returned 0 points. Retrieval failed. ---")
        return "", []

    # --- RERANKING STAGE: Use Cohere rerank to improve relevance ---
    logger.debug(f"--- DEBUG: Starting Cohere reranking on {len(results['points'])} candidates ---")
    
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
        logger.debug(f"--- DEBUG: Reranking complete. Top {len(reranked_results)} results selected ---")
    except Exception as e:
        logger.error(f"--- WARNING: Reranking failed: {e}. Using original Qdrant order. ---")
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
        logger.debug(f'--- DEBUG: Reranked Resume {cnt_resume}: {source}, Score: {score:.3f} ---')
        
        # Pass full resume but cap total context size
        data = f"Resume-{cnt_resume} ({source})\n\n{page_content}"  # Limit to 2000 chars per resume
        all_docs_data += data + "\n\n---\n\n"
        cnt_resume += 1

    logger.debug(f"--- DEBUG: Total context length for LLM: {len(all_docs_data)} tokens (approx {len(all_docs_data)//4}) ---")
    logger.debug(f"--- DEBUG: Selected Files for Download: {selected_files} ---")
  
    return all_docs_data, selected_files


def initialize_app_data():
    logger.info("--- Initializing collections and data... ---")

    if qdrant_client is None:
        raise RuntimeError("Qdrant qdrant_client is not initialized. Check QDRANT_URL, QDRANT_API_KEY and network connectivity.")

    if not qdrant_client.collection_exists("resumes"):
        logger.info("--- Creating 'resumes' collection ---")
        qdrant_client.create_collection(
            collection_name="resumes",
            vectors_config=VectorParams(
                size=1536,
                distance=Distance.COSINE,
                hnsw_config=HnswConfigDiff(m=16, ef_construct=128, full_scan_threshold=10000),
                on_disk=False
            )
        )
        
        qdrant_client.create_payload_index(collection_name="resumes", field_name='source', field_schema=rest.PayloadSchemaType.KEYWORD)
        
    # Initialize 'history' collection
    if not qdrant_client.collection_exists("history"):
        logger.info("--- Creating 'history' collection ---")
        qdrant_client.create_collection(
            collection_name="history",
            vectors_config=VectorParams(size=1536, distance=Distance.COSINE, on_disk=False)
        )
        # Create payload index for user_id so filters/deletes by user_id are supported
        try:
            qdrant_client.create_payload_index(collection_name="history", field_name="user_id", field_schema=rest.PayloadSchemaType.KEYWORD)
            qdrant_client.create_payload_index(collection_name="history", field_name="chat_group_id", field_schema=rest.PayloadSchemaType.KEYWORD)
            logger.info("Created payload index 'user_id' and 'chat_group_id' on 'history' collection")
        except Exception as e:
            logger.error(f"Warning: failed to create payload index for history.user_id and/or history.chat_group_id: {e}")
    logger.info("--- Initial app data setup complete. ---")

