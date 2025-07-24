# backend/app/crud/user_crud.py (SIMPLIFIED & SYNCHRONOUS CRUD)
from sqlalchemy.orm import Session # Import synchronous Session
from sqlalchemy import select # Still use select for query construction
from app.models.users import User
from app.schemas.user_schemas import UserCreate
from uuid import UUID

class CRUDUser:
    def get_by_email(self, db: Session, email: str) -> User | None: # <--- No 'async'
        # --- YAHAN CHANGE HAI ---
        return db.execute(select(User).filter(User.email == email)).scalars().first() # No 'await'
        # --- END CHANGE ---

    def get_by_id(self, db: Session, user_id: UUID) -> User | None: # <--- No 'async'
        # --- YAHAN CHANGE HAI ---
        return db.execute(select(User).filter(User.id == user_id)).scalars().first() # No 'await'
        # --- END CHANGE ---

    def create(self, db: Session, user_in: UserCreate, hashed_password: str) -> User: # <--- No 'async'
        db_user = User(
            name=user_in.name,
            email=user_in.email,
            hashed_password=hashed_password,
            is_active=True
        )
        # --- YAHAN CHANGE HAI ---
        db.add(db_user)
        db.commit() # No 'await'
        db.refresh(db_user) # No 'await'
        # --- END CHANGE ---
        return db_user

user_crud = CRUDUser()