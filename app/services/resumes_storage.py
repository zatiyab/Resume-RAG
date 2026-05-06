from functools import lru_cache
from typing import Any
from supabase import create_client
from app.core.config import settings


@lru_cache(maxsize=1)
def get_supabase_client() -> Any:
    """Lazily create and cache a Supabase client instance.

    Using a function avoids creating the client at import time which makes
    testing and startup ordering easier.
    """
    return create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)


def get_resume_url(file_path: str) -> str:
    supabase = get_supabase_client()
    response = supabase.storage.from_("Resumes").create_signed_url(
        path=file_path,
        expires_in=3600,  # 1 hour
    )
    return response["signedURL"]


def list_user_resumes(user_id: str) -> list[dict]:
    supabase = get_supabase_client()
    response = supabase.storage.from_("Resumes").list(user_id)
    return response


def delete_resume(file_path: str) -> None:
    supabase = get_supabase_client()
    supabase.storage.from_("Resumes").remove([file_path])


def download_resume_bytes(file_path: str) -> bytes:
    """Return the raw bytes for a stored resume."""
    supabase = get_supabase_client()
    return supabase.storage.from_("Resumes").download(file_path)


def upload_resume(file_bytes: bytes, user_id: str, resume_name: str) -> str:
    """Upload a resume; raises `ValueError` if a file with same name exists."""
    supabase = get_supabase_client()
    file_path = f"{user_id}/{resume_name}"
    existing_files = list_user_resumes(user_id)
    existing_names = [f.get("name") if isinstance(f, dict) else getattr(f, "name", None) for f in existing_files]
    print(f"Existing files for user {user_id}: {len(existing_names)}")
    if resume_name in existing_names:
        raise ValueError(f"A resume with the name '{resume_name}' already exists for this user. Skipping upload.")

    supabase.storage.from_("Resumes").upload(
        path=file_path,
        file=file_bytes,
        file_options={"content-type": "application/pdf"},
    )

    return file_path
