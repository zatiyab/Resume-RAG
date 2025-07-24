# backend/app/crud/user_crud.py (FINAL SYNCHRONOUS VERSION - No async/await)
from sqlalchemy.orm import Session # Import synchronous Session
from sqlalchemy import select # Still use select for query construction
from app.models.users import User
from app.schemas.user_schemas import UserCreate
from uuid import UUID
# REMOVE: import asyncio # Make sure this is NOT here

class CRUDUser:
    # CONFIRM: Methods are 'def', NOT 'async def'
    def get_by_email(self, db: Session, email: str) -> User | None:
        # CONFIRM: No 'await' here
        result = db.execute(select(User).filter(User.email == email))
        return result.scalars().first()

    def get_by_id(self, db: Session, user_id: UUID) -> User | None:
        # CONFIRM: No 'await' here
        result = db.execute(select(User).filter(User.id == user_id))
        return result.scalars().first()

    def create(self, db: Session, user_in: UserCreate, hashed_password: str) -> User:
        db_user = User(
            name=user_in.name,
            email=user_in.email,
            hashed_password=hashed_password,
            is_active=True
        )
        # CONFIRM: No 'await' for db.add, db.commit, db.refresh
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user

user_crud = CRUDUser()