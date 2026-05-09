from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status
from sqlalchemy.orm import Session
from app.api.dependencies import get_db_with_retry
from app.crud.user_resumes_crud import list_resumes_by_user_id
from app.schemas.req_models import DownloadRequest
from fastapi.responses import StreamingResponse
import zipfile
import io
import asyncio
import re
from pathlib import Path
import httpx

from app.schemas.req_models import DownloadRequest

from app.services.resumes_storage import download_resume_bytes as download_resume_bytes_from_storage
from app.services.qdrant_client import add_vectors, SUPPORTED_RESUME_EXTENSIONS

router = APIRouter(tags=["resumes"])


@router.get("/resumes")
async def list_resumes(user_id: str, db: Session = Depends(get_db_with_retry)):
    try:
        resumes = list_resumes_by_user_id(user_id, db)
        print(f"Resumes for user {user_id}: {resumes}")
        return {"resumes": resumes}
    except Exception as e:
        print(f"Error listing resumes for user {user_id}: {e}")
        raise HTTPException(status_code=500, detail="Error retrieving resume list")


@router.get("/resume")
async def get_resume(user_id: str, file_name: str):
    try:
        file_path = f"{file_name}"
        file_bytes = await asyncio.to_thread(download_resume_bytes_from_storage, file_path)
        if not file_bytes:
            raise HTTPException(status_code=404, detail="File not found")
        import io as _io
        import mimetypes
        mime, _ = mimetypes.guess_type(file_name)
        media_type = mime or 'application/octet-stream'
        return StreamingResponse(_io.BytesIO(file_bytes), media_type=media_type, headers={"Content-Disposition": f"inline; filename=\"{file_name}\""})
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error fetching resume {file_name} for user {user_id}: {e}")
        raise HTTPException(status_code=500, detail="Error retrieving resume file")


@router.post("/upload_resumes")
async def upload_resumes(files: list[UploadFile] = File(...), user_id: str = None,db: Session = Depends(get_db_with_retry)):
    # Debug: log incoming file info to help diagnose empty uploads
    from app.services.resumes_storage import upload_resume as upload_resume_to_storage
    from app.rag_logic.utils import convert_doc_content_to_pdf_bytes

    try:
        file_names = [f.filename for f in files] if files else []
    except Exception:
        file_names = []
    print(f"upload_resumes called for user_id={user_id} with {len(file_names)} files: {file_names}")

    if not files:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No files provided")

    is_duplicate = []
    saved_files: list[str] = []
    skipped_files: list[dict] = []

    for uploaded_file in files:
        filename = uploaded_file.filename or ""
        suffix = Path(filename).suffix.lower()

        if suffix not in SUPPORTED_RESUME_EXTENSIONS:
            skipped_files.append({"file": filename, "reason": "unsupported extension"})
            continue

        safe_stem = re.sub(r"[^A-Za-z0-9._-]+", "_", Path(filename).stem).strip("._") or "resume"
        stored_name = f"{safe_stem}{suffix}"

        try:
            content = await uploaded_file.read()
            
            # Convert DOC/DOCX to PDF before uploading
            if suffix != ".pdf":
                content = await asyncio.to_thread(convert_doc_content_to_pdf_bytes, content, filename)
                stored_name = f"{safe_stem}.pdf"
            try:
                path = await asyncio.to_thread(upload_resume_to_storage, content, stored_name)
                print("Uploaded to Supabase at:", path)
            except ValueError as e:
                is_duplicate.append(stored_name)
                print(f"Duplicate file skipped: {stored_name} \n {e}")
                raise HTTPException(status_code=500, detail=f"Failed to upload {filename}: {e}")
            except Exception as e:
                print(f"Unexpected error occurred while uploading {stored_name}: {e}")
                raise HTTPException(status_code=500, detail=f"Failed to upload {filename}: {e}")
            else:
                saved_files.append(stored_name)
        except Exception as e:
            skipped_files.append({"file": stored_name, "reason": f"upload failed: {e}"})
        finally:
            await uploaded_file.close()

    if not saved_files and not is_duplicate:
        print(f"No saved files. Skipped files: {skipped_files}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": "No valid files were uploaded",
                "skipped_files": skipped_files,
            },
        )

    # Pass the newly uploaded files to add_vectors to avoid redundant Supabase fetch
    # and duplicate checks - we already know these files are new
    if is_duplicate:
        print(f"Duplicate file names detected during upload. Skipped files: {skipped_files}")

    ingestion_result = await asyncio.to_thread(add_vectors,
                                               user_id=user_id, 
                                               files_to_process=saved_files,
                                               db=db, 
                                               duplicate_files=is_duplicate)

    return {
        "message": "Resumes uploaded and indexed successfully",
        "saved_files": saved_files,
        "skipped_files": skipped_files,
        "ingestion": ingestion_result,
    }


@router.post("/download_resumes")
async def download_resumes(request: DownloadRequest):
    if not request.files:
        raise HTTPException(status_code=400, detail="No files requested")
        
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w") as zip_file:
        for file_name in request.files:
            file_path = f"{file_name}"
            try:
                file_bytes = await asyncio.to_thread(download_resume_bytes_from_storage, file_path)
                zip_file.writestr(file_name, file_bytes)
            except Exception as e:
                print(f"Error downloading {file_name}: {e}")
                pass
                
        # Guard against shipping an empty ZIP if all files failed to be fetched
        if not zip_file.infolist():
            raise HTTPException(status_code=404, detail="None of the requested files were found on the server.")
                
    from fastapi import Response
    zip_buffer.seek(0)
    return Response(
        content=zip_buffer.getvalue(),
        media_type="application/x-zip-compressed",
        headers={"Content-Disposition": "attachment; filename=resumes.zip"}
    )



@router.delete("/resume")
async def remove_resume(user_id: str, file_name: str, db: Session = Depends(get_db_with_retry)):
    
    from app.crud.user_resumes_crud import delete_resume_from_file_name_user_id
    try:
        delete_resume_from_file_name_user_id(file_name, user_id, db)
        return {"message": f"Resume '{file_name}' deleted successfully"}
    except Exception as e:
        print(f"Error deleting resume {file_name} for user {user_id}: {e}")
        raise HTTPException(status_code=500, detail="Error deleting resume")


@router.delete("/clear_data")
async def clear_data(user_id: str,db: Session = Depends(get_db_with_retry)):
    """Clear all resumes and history vectors for a user from Qdrant collections."""

    from app.services.qdrant_client import qdrant_client as client
    from app.vector_crud.history_crud import delete_history_by_user_id as delete_history_by_user_id_from_qdrant
    from app.crud.chat_crud import delete_chat_history as delete_chat_history_from_db
    
    try:  
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get("http://localhost:5000/resumes", params={"user_id": user_id})
                data = response.json()
                for resume_name in data['resumes']:
                    await client.delete("http://localhost:5000/resume", params={"user_id": user_id, "file_name": resume_name})
        except Exception as e:
            print(f"Error clearing resumes from storage: {e}")            
        
        # Delete from history collection
        try:
            await asyncio.to_thread(delete_history_by_user_id_from_qdrant, user_id)
        except Exception as e:
            print(f"Error clearing history from Qdrant: {e}")

        try:
            delete_chat_history_from_db(user_id, db)
        except Exception as e:
            print(f"Error clearing chat history: {e}")

        return {"message": "Data deleted successfully"}
    except Exception as e:
        print(f"Error clearing data for user {user_id}: {e}")
        raise HTTPException(status_code=500, detail="Error clearing data")
    
