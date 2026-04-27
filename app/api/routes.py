import asyncio
import re
from pathlib import Path
from uuid import uuid4

from asyncpg.exceptions import DuplicatePreparedStatementError
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from sqlalchemy.orm import Session
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_fixed
from pydantic import BaseModel

from app.core.database import get_db
from app.crud.user_crud import user_crud
from app.schemas.req_models import ChatPost
from app.schemas.user_schemas import UserCreate, UserInDB, UserLogin
from app.services.auth_service import AuthService
from app.services.chat import post_chat_messages
from app.services.qdrant_client import add_vectors, get_resumes_dir, SUPPORTED_RESUME_EXTENSIONS


router = APIRouter()

@router.post("/")
async def post_chat(request:ChatPost,db:Session = Depends(get_db)):
    return await post_chat_messages(request,db)

def get_auth_service(db: Session = Depends(get_db)) -> AuthService: # <--- Change type hint to Session
    return AuthService(db)


retry_db_exception = retry(
    stop=stop_after_attempt(3),
    wait=wait_fixed(1),
    retry=retry_if_exception_type(DuplicatePreparedStatementError), # Still retry on this error type
    reraise=True
)

@router.post("/signup", response_model=UserInDB, status_code=status.HTTP_201_CREATED)
@retry_db_exception
async def signup_user(user_in: UserCreate, db: Session = Depends(get_db)): # <--- Change type hint to Session
    try:
        existing_user = await user_crud.get_by_email(db, email=user_in.email) 
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email already registered"
            )
        
        hashed_password = AuthService.get_password_hash(user_in.password)
        # user_crud.create is now async
        user = await user_crud.create(db, user_in=user_in, hashed_password=hashed_password)
        return user
    except HTTPException as e:
        raise e
    except Exception as e:
        print(f"ERROR: Unhandled exception during signup for email {user_in.email}: {type(e).__name__} - {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected server error occurred during signup. Please try again."
        )

@router.post("/login")
@retry_db_exception
async def login_user(user_in: UserLogin, auth_service: AuthService = Depends(get_auth_service)): # <--- Change type hint to Session
    try:
        user = await auth_service.authenticate_user(user_in.email, user_in.password)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        access_token = auth_service.create_access_token(data={"sub": str(user.id)})
        return {"access_token": access_token, "token_type": "bearer", "user_id": str(user.id)}
    except HTTPException as e:
        raise e
    except Exception as e:
        print(f"ERROR: Unhandled exception during login for email {user_in.email}: {type(e).__name__} - {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected server error occurred during login."
        )


class DownloadRequest(BaseModel):
    files: list[str]
    user_id: str

@router.post("/upload_resumes")
async def upload_resumes(files: list[UploadFile] = File(...), user_id: str = None):
    if not files:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No files provided")

    from app.services.resumes_storage import upload_resume
    from app.rag_logic.utils import convert_doc_content_to_pdf_bytes

    saved_files: list[str] = []
    skipped_files: list[dict] = []

    for uploaded_file in files:
        filename = uploaded_file.filename or ""
        suffix = Path(filename).suffix.lower()

        if suffix not in SUPPORTED_RESUME_EXTENSIONS:
            skipped_files.append({"file": filename, "reason": "unsupported extension"})
            continue

        safe_stem = re.sub(r"[^A-Za-z0-9._-]+", "_", Path(filename).stem).strip("._") or "resume"
        stored_name = f"{safe_stem}_{uuid4().hex[:8]}{suffix}"

        try:
            content = await uploaded_file.read()
            
            # Convert DOC/DOCX to PDF before uploading
            if suffix != ".pdf":
                content = await asyncio.to_thread(convert_doc_content_to_pdf_bytes, content, filename)
                stored_name = f"{safe_stem}_{uuid4().hex[:8]}.pdf"

            path = await asyncio.to_thread(upload_resume, content, user_id, stored_name)
            print("Uploaded to Supabase at:", path)
            saved_files.append(stored_name)
        except Exception as e:
            skipped_files.append({"file": filename, "reason": f"upload failed: {e}"})
        finally:
            await uploaded_file.close()

    if not saved_files:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": "No valid files were uploaded",
                "skipped_files": skipped_files,
            },
        )

    ingestion_result = await asyncio.to_thread(add_vectors, user_id=user_id)

    return {
        "message": "Resumes uploaded and indexed successfully",
        "saved_files": saved_files,
        "skipped_files": skipped_files,
        "ingestion": ingestion_result,
    }


from fastapi.responses import StreamingResponse
import zipfile
import io
from app.services.resumes_storage import download_resume_bytes

@router.post("/download_resumes")
async def download_resumes(request: DownloadRequest):
    if not request.files:
        raise HTTPException(status_code=400, detail="No files requested")
        
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w") as zip_file:
        for file_name in request.files:
            file_path = f"{request.user_id}/{file_name}"
            try:
                file_bytes = await asyncio.to_thread(download_resume_bytes, file_path)
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
