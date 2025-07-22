# data_processing.py
import re 
import unicodedata
import time
import os
import pdfplumber
import json
from langchain_huggingface import HuggingFaceEmbeddings # Not used, can remove
from qdrant_client.http.models import PointStruct
from langchain_cohere import ChatCohere
from qdrant_client import QdrantClient
from sentence_transformers import SentenceTransformer
from convert_to_pdf import convert_all_docs_in_folder

# print("This is the Cohere key in data processing:", os.getenv('COHERE_API_KEY'))
# llm = ChatCohere(model="command-r-plus",timeout_seconds=60,cohere_api_key=os.getenv('COHERE_API_KEY'))
llm = ChatCohere(model="command-r-plus",timeout_seconds=60,cohere_api_key="BCxkxzdkBAiA9Ey0mS7csgHSRxaV2YHcYu6mtTrg")
print(os.getenv('COHERE_API_KEY'))

embedding = SentenceTransformer("BAAI/bge-large-en-v1.5")
client = QdrantClient(
    url="http://localhost:6333",
    timeout=60.0
)



def remove_same_files(folder):
    import re
    pattern = r"\(\d+\)$"
    resumes = os.listdir(folder)
    resumes = [i for i in resumes if i.endswith('.pdf')]
    for resume in resumes:
        resume = resume.rstrip('.pdf')
        if re.search(pattern,resume):
            print('Copy : ',resume)


def basic_text_normalization(text: str) -> str:
    """Basic cleaning that should be applied to all text"""
    
    # Remove or normalize unicode characters
    text = unicodedata.normalize('NFKD', text)
    
    # Fix common encoding issues
    text = text.encode('ascii', 'ignore').decode('ascii')
    
    # Remove excessive whitespace
    text = re.sub(r'\s+', ' ', text)
    
    # Remove special characters but keep meaningful punctuation
    text = re.sub(r'[^\w\s\-\.\,\(\)\/]', '', text)
    
    # Normalize case (but preserve acronyms)
    words = text.split()
    normalized_words = []
    for word in words:
        if word.isupper() and len(word) > 1:  # Keep acronyms
            normalized_words.append(word)
        else:
            normalized_words.append(word.lower())
    
    return ' '.join(normalized_words).strip()

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


def add_vectors():
    '''
    Reads all the resumes in the resumes folder extracts text and calls function to generate metadata 
    then converts the resume into a vector and save it into the resume collection along with their respective metadatas.
    '''

    convert_all_docs_in_folder("resumes")
    resumes = os.listdir('resumes')
    all_vec = client.scroll(collection_name='resumes',with_payload=['source'],limit=1000000)
    print(all_vec[0],flush = True)
    try:
        files_vector = [i.payload['source'] for i in all_vec[0]]
        last_indx = all_vec[0][-1].id
    except:
        files_vector = []
        last_indx = 0
    print('Last Vector Index: ',last_indx,flush = True)
    print('Existing Vectors: ',files_vector)
    resumes = [i for i in resumes if i not in files_vector]
    files_vector.extend(resumes)
    print('Total No. of resumes: ',len(resumes))
    
    points = []
    resumes_data_dict = {}
    for resume in resumes:
        resume_data =''
        with pdfplumber.open('resumes/'+resume) as pdf:
            for i, page in enumerate(pdf.pages):
                text = page.extract_text()
                if text:
                    resume_data+=text.strip()
                else:
                    print("No text found.")

                # Attempt to extract tables
                tables = page.extract_tables()
                if tables:
                    
                    tables_data = ''
                    for table in tables:
                        table_str = "\n".join([" | ".join([str(cell) if cell is not None else "" for cell in row]) for row in table])
                        tables_data +=('\n'+table_str)
                    
                    resume_data+=tables_data
        if resume_data not in resumes_data_dict.values():
            resumes_data_dict[resume]= resume_data
    
    for resume,resume_data in resumes_data_dict.items():
        last_indx+=1
        resume_data= basic_text_normalization(resume_data)
        metadata_dict = llm_create_metadata(resume_data.lower(),resume_name=resume)
        vector = embedding.encode(resume_data)
        vector_str = json.dumps(vector.tolist())
    
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
        
        points.append(PointStruct(id=last_indx, vector=vector, payload=metadata_dict))        
        print(f'At {last_indx}/{len(resumes_data_dict)}, {resume}') # Use len(resumes_data_dict) for total unique resumes processed

    if points: # Check if points list is not empty
        operation_info = client.upsert(
                collection_name="resumes",
                wait=True,
                points=points
            )
        print(operation_info)
    



def delete_collection():
    client.delete_collection('resumes',timeout=3)