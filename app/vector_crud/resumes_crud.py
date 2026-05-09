from app.clients import get_qdrant
from qdrant_client.models import MatchValue, PointStruct, Filter, FieldCondition
from app.services.qdrant_client import _embed_text

qdrant_client = get_qdrant()

def batch_add_resumes(resume_names: list, resume_texts: list, resume_vector_ids: list):
    '''
    Get a list of resume texts and converts them into vectors
    and also adds them to the vector resume db and prints the result of the upsert operation
    '''
    BATCH_SIZE = 20
    points = []
    batch_operations_info = []

    for resume_name, resume_text, vector_id in zip(resume_names, resume_texts, resume_vector_ids):
    
        # Use search_document input type for resume embeddings (better for retrieval)
        vector = _embed_text(resume_text, input_type="search_document")
    
        metadata_dict = {'source': resume_name, 'page_content': resume_text}  
        
        points.append(PointStruct(id=vector_id, vector=vector, payload=metadata_dict))

    if points:
        num_batches = (len(points) + BATCH_SIZE - 1) // BATCH_SIZE
        print(f"Upserting in batches of {BATCH_SIZE}. Total batches: {num_batches}")
        for batch_start in range(0, len(points), BATCH_SIZE):
            batch_points = points[batch_start:batch_start + BATCH_SIZE]
            operation_info = qdrant_client.upsert(
                collection_name="resumes",
                wait=True,
                points=batch_points
            )
            print(operation_info)
            batch_operations_info.append(operation_info)
    return batch_operations_info

def get_resumes_with_source(user_id: str) -> list[dict]:
    '''
    Retrieves all resume vectors for a user and returns a list of dicts with source and page_content
    '''
    try:
        all_resumes_for_user = qdrant_client.scroll(
                collection_name='resumes',
                scroll_filter=Filter(must=[FieldCondition(key="user_id", match=MatchValue(value=user_id))]),
                with_payload=['source'],
                limit=1000000
            )
        return [
            result.payload.get("source")
            for result in all_resumes_for_user[0]
        ]
    except Exception as e:
        print(f"Error fetching resumes for user {user_id}: {e}")
        return []
    
def delete_resumes_by_user_id(user_id: str):
    '''
    Deletes all resume vectors for a user from the vector resume db based on user_id and prints the result of the delete operation
    '''
    try:
        user_filter = Filter(
            must=[FieldCondition(key="user_id", match=MatchValue(value=user_id))]
        )
        operation_info = qdrant_client.delete(
            collection_name="resumes",
            points_selector=user_filter
        )
        print(f"--- DEBUG: Resumes Deleted for user {user_id}: {operation_info} ---")
    except Exception as e:
        print(f"Error deleting resumes for user {user_id}: {e}")

def get_similar_resumes(user_query, user_id,must_conditions, k=5):
    '''
    Retrieves similar resumes for a user based on a query and returns a list of resume sources
    '''
    try:
        try:
            # Use search_query input type for better alignment with search_document embeddings
            query_embedding = _embed_text(user_query.lower(), input_type="search_query")
            print(f"--- DEBUG: Query embedding generated successfully, vector size: {len(query_embedding)} ---")
        except Exception as e:
            print(f"--- ERROR: Failed to embed query: {e} ---")
            return []
        
        
        search_result = qdrant_client.query_points(
            collection_name="resumes",
            query=query_embedding,
            limit=int(min(k * 2, 50)),  # Retrieve 2x K for reranking, max 50
            query_filter=Filter(
                must=must_conditions
            ),
            score_threshold=0.0  # Remove threshold initially to see all results
        )
        return search_result
    except Exception as e:
        print(f"Error fetching similar resumes for user {user_id}: {e}")
        return []
    
def remove_resume_from_qdrant(user_id, file_name):
    try:
        delete_filter = Filter(
            must=[
                FieldCondition(key="user_id", match=MatchValue(value=user_id)),
                FieldCondition(key="source", match=MatchValue(value=file_name))
            ]
        )
        delete_result = qdrant_client.delete(
            collection_name="resumes",
            points_selector=delete_filter
        )
        print(f"Deleted resume '{file_name}' for user '{user_id}' from Qdrant: {delete_result}")
    except Exception as e:
        print(f"Error deleting resume '{file_name}' for user '{user_id}' from Qdrant: {e}")
