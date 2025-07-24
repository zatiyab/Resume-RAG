
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.models.users import User
from app.schemas.user_schemas import UserCreate
from uuid import UUID
import asyncio

class CRUDUser:
    async def get_by_email(self, db: Session, email: str) -> User | None:
        # --- YAHAN CHANGE HAI ---
        result = await asyncio.to_thread(db.execute, select(User).filter(User.email == email))
        return result.scalars().first()
        # --- END CHANGE ---

    async def get_by_id(self, db: Session, user_id: UUID) -> User | None:
        # --- YAHAN CHANGE HAI ---
        result = await asyncio.to_thread(db.execute, select(User).filter(User.id == user_id))
        return result.scalars().first()
        # --- END CHANGE ---

    async def create(self, db: Session, user_in: UserCreate, hashed_password: str) -> User:
        db_user = User(
            name=user_in.name,
            email=user_in.email,
            hashed_password=hashed_password,
            is_active=True
        )
        # --- YAHAN CHANGE HAI ---
        await asyncio.to_thread(db.add, db_user)
        await asyncio.to_thread(db.commit)
        await asyncio.to_thread(db.refresh, db_user)
        # --- END CHANGE ---
        return db_user

user_crud = CRUDUser()