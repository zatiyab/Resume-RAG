# backend/app/api/routes.py (FINAL ROUTER VERSION - Correct asyncio.to_thread)
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.users import User
from app.schemas.user_schemas import UserCreate, UserLogin, UserInDB
from app.crud.user_crud import user_crud # CRUD methods are synchronous
from app.services.auth_service import AuthService # Auth service methods are synchronous
from tenacity import retry, stop_after_attempt, wait_fixed, retry_if_exception_type
# If you no longer need this specific exception for tenacity, remove it.
# from asyncpg.exceptions import DuplicatePreparedStatementError 

import asyncio # <--- YAHAN CHANGE HAI: Import asyncio for to_thread

auth_router = APIRouter()

def get_auth_service(db: Session = Depends(get_db)) -> AuthService:
    return AuthService(db)

# If DuplicatePreparedStatementError is gone, you can simplify retry to just retry on Exception or remove it
retry_db_exception = retry(
    stop=stop_after_attempt(3),
    wait=wait_fixed(1),
    # CONFIRM: If DuplicatePreparedStatementError is gone, change this to Exception
    # retry=retry_if_exception_type(DuplicatePreparedStatementError), 
    retry=retry_if_exception_type(Exception), # <--- YAHAN CHANGE HAI: Retry on generic Exception
    reraise=True
)

@auth_router.post("/signup", response_model=UserInDB, status_code=status.HTTP_201_CREATED)
@retry_db_exception
async def signup_user(user_in: UserCreate, db: Session = Depends(get_db)):
    try:
        with db.begin():
            # CONFIRM: Call synchronous CRUD methods using await asyncio.to_thread()
            existing_user = await asyncio.to_thread(user_crud.get_by_email, db, email=user_in.email)
            if existing_user:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Email already registered"
                )
            
            hashed_password = AuthService.get_password_hash(user_in.password) # This is a static method, no asyncio.to_thread
            user = await asyncio.to_thread(user_crud.create, db, user_in=user_in, hashed_password=hashed_password)
            return user
    except HTTPException as e:
        raise e
    except Exception as e:
        print(f"ERROR: Unhandled exception during signup for email {user_in.email}: {type(e).__name__} - {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected server error occurred during signup. Please try again."
        )

@auth_router.post("/login")
@retry_db_exception
async def login_user(user_in: UserLogin, auth_service: AuthService = Depends(get_auth_service)):
    try:
        with auth_service.db.begin():
            # CONFIRM: Call synchronous auth service method using await asyncio.to_thread()
            user = await asyncio.to_thread(auth_service.authenticate_user, user_in.email, user_in.password)
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Incorrect email or password",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            access_token = auth_service.create_access_token(data={"sub": str(user.id)}) # This is sync method, no await
            return {"access_token": access_token, "token_type": "bearer"}
    except HTTPException as e:
        raise e
    except Exception as e:
        print(f"ERROR: Unhandled exception during login for email {user_in.email}: {type(e).__name__} - {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected server error occurred during login."
        )