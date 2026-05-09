from app.clients import get_supabase_client
from app.core.logger import logger





def get_resume_url(file_path: str) -> str:
    supabase = get_supabase_client()
    response = supabase.storage.from_("Resumes").create_signed_url(
        path=file_path,
        expires_in=3600,  # 1 hour
    )
    return response["signedURL"]


def list_user_resumes() -> list[dict]:
    supabase = get_supabase_client()
    page_size = 100
    offset = 0
    all_files: list[dict] = []

    while True:
        response = supabase.storage.from_("Resumes").list(
            path="",
            options={"limit": page_size, "offset": offset},
        )

        # Supabase client may return (data, error), dict error, or just a list.
        if isinstance(response, tuple) and len(response) == 2:
            data, err = response
            if err:
                logger.error(f"Error listing resumes from Supabase: {err}")
                return all_files
            page = data or []
        elif isinstance(response, dict) and response.get("statusCode") is not None:
            logger.error(f"Error listing resumes from Supabase: {response}")
            return all_files
        else:
            page = response or []

        all_files.extend(page)

        if len(page) < page_size:
            break
        offset += page_size

    return all_files


def delete_resume(file_path: str) -> None:
    supabase = get_supabase_client()
    supabase.storage.from_("Resumes").remove([file_path])


def download_resume_bytes(file_path: str) -> bytes:
    """Return the raw bytes for a stored resume."""
    supabase = get_supabase_client()
    resp = supabase.storage.from_("Resumes").download(file_path)
    # The Supabase client may return a dict with error info when the object
    # is not found (e.g. {'statusCode': 404, 'error': 'not_found', ...}).
    # Normalize this to `None` so the calling route can return a 404.
    if isinstance(resp, dict) and resp.get("statusCode") is not None:
        logger.error(f"Failed to download {file_path} from Supabase: {resp}")
        return None
    return resp


def upload_resume(file_bytes: bytes, resume_name: str) -> str:
    """Upload a resume; raises `ValueError` if a file with same name exists."""
    supabase = get_supabase_client()
    file_path = f"{resume_name}"
    existing_files = list_user_resumes()
    existing_names = [f.get("name") if isinstance(f, dict) else getattr(f, "name", None) for f in existing_files]
    logger.debug(f"Existing files: {len(existing_names)}")
    if resume_name in existing_names:
        raise ValueError(f"A resume with the name '{resume_name}' already exists. Skipping upload.")
    upload_resp = supabase.storage.from_("Resumes").upload(
        path=file_path,
        file=file_bytes,
        file_options={"content-type": "application/pdf"},
    )

    # Check upload response for errors (client may return dict or (data, error)).
    if isinstance(upload_resp, tuple) and len(upload_resp) == 2:
        data, err = upload_resp
        if err:
            logger.error(f"Supabase upload error for {file_path}: {err}")
            raise RuntimeError(f"Failed to upload {file_path}: {err}")
    elif isinstance(upload_resp, dict) and upload_resp.get("statusCode") is not None:
        logger.error(f"Supabase upload error for {file_path}: {upload_resp}")
        raise RuntimeError(f"Failed to upload {file_path}: {upload_resp}")


    return file_path
