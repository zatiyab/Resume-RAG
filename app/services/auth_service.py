from app.core.logger import logger
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
    def __init__(self, db: Session): 
        self.db = db

    @staticmethod
    def get_password_hash(password: str) -> str:
        return pwd_context.hash(password)

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        return pwd_context.verify(plain_password, hashed_password)

    
    async def authenticate_user(self, email: str, password: str) -> Optional[User]: 
        # user_crud.get_by_email is async - await it
        user = await user_crud.get_by_email(self.db, email=email)
        if not user or not self.verify_password(password, user.hashed_password):
            return None
        return user
    
    def create_access_token(self, data: dict, expires_delta: Optional[timedelta] = None) -> str:
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.now(timezone.utc) + expires_delta
        else:
            expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
        return encoded_jwt

    @staticmethod
    def verify_token(token: str) -> Optional[str]:
        """
        Verify JWT token and return the user_id (sub claim).
        Returns None if token is invalid or expired.
        """
        try:
            logger.debug(f"[TOKEN DEBUG] Decoding token with SECRET_KEY (first 20 chars): {settings.SECRET_KEY[:20]}...")
            logger.debug(f"[TOKEN DEBUG] Using algorithm: {settings.ALGORITHM}")
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
            logger.debug(f"[TOKEN DEBUG] Token decoded successfully. Payload: {payload}")
            user_id: str = payload.get("sub")
            if user_id is None:
                logger.debug("[TOKEN DEBUG] Token payload missing 'sub' claim")
                raise JWTError("Token payload missing 'sub' claim")
            logger.debug(f"[TOKEN DEBUG] Extracted user_id: {user_id}")
            return user_id
        except JWTError as e:
            logger.error(f"[TOKEN DEBUG] JWTError: {str(e)}")
            return None
    
    def refresh_access_token(self, token: str) -> Optional[str]:
        """
        Refresh an access token by verifying the old token and issuing a new one.
        Returns the new token if successful, or None if the old token is invalid.
        """
        user_id = self.verify_token(token)
        if user_id is None:
            return None
        new_token = self.create_access_token(data={"sub": user_id})
        return new_token