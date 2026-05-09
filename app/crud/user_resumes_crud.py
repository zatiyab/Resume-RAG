from app.models.user_resumes import UserResume
from app.models.resumes import Resume

def add_user_resumes(user_id, resume_id, db):
    user_resume = UserResume(user_id=user_id, resume_id=resume_id)
    db.add(user_resume)
    db.commit()
    db.refresh(user_resume)
    return user_resume

def delete_user_resumes_by_user_id(user_id, db):
    db.query(UserResume).filter(UserResume.user_id == user_id).delete()
    db.commit()

def delete_user_resumes_by_resume_id(resume_id, db):
    db.query(UserResume).filter(UserResume.resume_id == resume_id).delete()
    db.commit()

def list_resumes_by_user_id(user_id, db):
    db_query = db.query(Resume.resume_name)
    db_query = db_query.select_from(UserResume)
    db_query = db_query.join(Resume, UserResume.resume_id == Resume.id)
    db_query = db_query.filter(UserResume.user_id == user_id)
    return [resume_name for (resume_name,) in db_query.all()]

def delete_user_resumes_by_user_resume_id(user_resume_id, db):
    db.query(UserResume).filter(UserResume.id == user_resume_id).delete()
    db.commit()

def delete_resume_from_file_name_user_id(file_name, user_id, db):
    db_query = db.query(UserResume)
    db_query = db_query.select_from(Resume)
    db_query = db_query.join(UserResume, Resume.id == UserResume.resume_id)
    db_query = db_query.filter(UserResume.user_id == user_id, Resume.resume_name == file_name)
    user_resume = db_query.first()
    if user_resume:
        delete_user_resumes_by_user_resume_id(user_resume.id, db)

def duplicate_resume_check(file_name, user_id, db):
    db_query = db.query(Resume.resume_name)
    db_query = db_query.select_from(UserResume)
    db_query = db_query.join(Resume, UserResume.resume_id == Resume.id)
    db_query = db_query.filter(UserResume.user_id == user_id, Resume.resume_name == file_name)
    return db_query.first() is not None