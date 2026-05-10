from app.models.resumes import Resume


def add_resume(file_path, resume_name, skills=None, experience_years=None, raw_location=None, state=None, city=None, name=None, resume_vector_id=None, db=None):
    resume = Resume(
        file_path=file_path,
        resume_name=resume_name,
        skills=skills,
        experience_years=experience_years,
        raw_location=raw_location,
        state=state,
        city=city,
        name=name,
        resume_vector_id=resume_vector_id
    )
    db.add(resume)
    db.commit()
    db.refresh(resume)
    return resume

def get_cnt_resumes(db):
    return db.query(Resume).count()

def find_resume_id_for_duplicate(file_name, db):
    resume = db.query(Resume).filter(Resume.resume_name == file_name).first()
    if resume:
        print(f"Found existing resume in DB for duplicate file '{file_name}': ID {resume.id}")
        return resume.id
    print(f"No existing resume found in DB for duplicate file '{file_name}'")
    return None

def list_resumes(db):
    return db.query(Resume).all()

def get_resume_id_by_vector_id(vector_id, db):
    resume = db.query(Resume).filter(Resume.resume_vector_id == vector_id).first()
    return resume.id if resume else None