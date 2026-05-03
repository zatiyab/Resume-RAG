from supabase import create_client
from app.core.config import settings


supabase = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)



def get_resume_url(file_path):
    response = supabase.storage.from_("Resumes").create_signed_url(
        path=file_path,
        expires_in=3600  # 1 hour
    )
    return response["signedURL"]


def list_user_resumes(user_id):
    response = supabase.storage.from_("Resumes").list(user_id)
    return response


def delete_resume(file_path):
    supabase.storage.from_("Resumes").remove([file_path])


def download_resume_bytes(file_path):
    # Returns the binary stream byte data directly
    return supabase.storage.from_("Resumes").download(file_path)

def upload_resume(file_bytes, user_id, resume_name):
    file_path = f"{user_id}/{resume_name}"
    # Check if file with the same path already exists
    existing_files = list_user_resumes(user_id)
    existing_names = [f.get('name') if isinstance(f, dict) else getattr(f, 'name', None) for f in existing_files]
    print(f"Existing files for user {user_id}: {existing_names}")
    if resume_name in existing_names:
        raise ValueError(f"A resume with the name '{resume_name}' already exists for this user. Skipping upload.")

    response = supabase.storage.from_("Resumes").upload(
        path=file_path,
        file=file_bytes,
        file_options={"content-type": "application/pdf"}
    )
    return file_path
