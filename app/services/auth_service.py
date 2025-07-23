# backend/app/services/auth_service.py (UPDATED for Synchronous Auth Service)
from datetime import datetime, timedelta, timezone
from typing import Optional
from passlib.context import CryptContext
from sqlalchemy.orm import Session # <--- Import synchronous Session
from app.core.config import settings
from app.models.users import User
from app.crud.user_crud import user_crud # user_crud methods are now synchronous
from jose import JWTError, jwt
import asyncio
# Password hashing context (using bcrypt)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class AuthService:
    def __init__(self, db: Session): # <--- Change type hint to Session
        self.db = db

    @staticmethod
    def get_password_hash(password: str) -> str:
        return pwd_context.hash(password)

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        return pwd_context.verify(plain_password, hashed_password)

    # --- YAHAN CHANGE HAI (no 'await' for user_crud.get_by_email) ---
    async def authenticate_user(self, email: str, password: str) -> Optional[User]: # <--- Add async
        user = await user_crud.get_by_email(self.db, email=email) # <--- Add await
        if not user or not self.verify_password(password, user.hashed_password):
            return None
        return user
    # --- END CHANGE ---

    def create_access_token(self, data: dict, expires_delta: Optional[timedelta] = None) -> str:
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.now(timezone.utc) + expires_delta
        else:
            expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
        return encoded_jwt