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
One or two sentences capturing the candidate's profile. If absent, write: _Not provided._

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
    except Exception as e:
        print(f"Error occurred while summarizing resume: {e}")
        summarized_resume = "Error occurred while summarizing resume."

    return summarized_resume.content.strip() if summarized_resume and summarized_resume.content else "No summary available."


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
        
    
    user_resumes_vec_cnt = len(files_vector)
    print('Last Vector Index for user ', user_id, ': ', user_resumes_vec_cnt, flush=True)
    print('Existing Vectors for user ', user_id, ': ', files_vector)

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
        user_resumes_vec_cnt+=1
        resume_data= basic_text_normalization(resume_data)
        resume_data = llm_summarize_resume(resume_data)
        vector = _embed_text(resume_data)
    
        metadata_dict = {'source': resume, 'page_content': resume_data,'user_id': user_id}  
        
        points.append(PointStruct(id=user_resumes_vec_cnt, vector=vector, payload=metadata_dict))
        print(f'At {user_resumes_vec_cnt}/{len(resumes_data_dict)}, {resume}') 
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
        add_vectors(user_id=user_id) 

        # keyword_lst = ["user_id", "name", "email", "phone", "location", "current_job_title", "current_company", "current_employment_location", "degree_major", "skills_total_keywords", "spoken_languages", "availability_for_joining"]

        # client.create_payload_index(collection_name="resumes", field_name="total_years_of_experience", field_schema=rest.PayloadSchemaType.FLOAT)
        # client.create_payload_index(collection_name="resumes", field_name="graduation_year", field_schema=rest.PayloadSchemaType.INTEGER)
        # for k in keyword_lst:
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


