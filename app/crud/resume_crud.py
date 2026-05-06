from app.models.resumes import ResumesMetadata


def add_resume_metadata(user_id, file_path, resume_name, skills=None, experience_years=None, raw_location=None, state=None, city=None, domain=None, name=None, resume_vector_id=None, db=None):
    resume_metadata = ResumesMetadata(
        user_id=user_id,
        file_path=file_path,
        resume_name=resume_name,
        skills=skills,
        experience_years=experience_years,
        raw_location=raw_location,
        state=state,
        city=city,
        domain=domain,
        name=name,
        resume_vector_id=resume_vector_id
    )
    db.add(resume_metadata)
    db.commit()
    db.refresh(resume_metadata)
    return resume_metadata

