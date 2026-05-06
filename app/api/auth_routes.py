from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_db_with_retry, get_auth_service,retry_db_exception

from app.schemas.user_schemas import UserInDB, UserCreate, UserLogin

from app.services.auth_service import AuthService

from app.crud.user_crud import user_crud

router = APIRouter()


@router.post("/signup", response_model=UserInDB, status_code=status.HTTP_201_CREATED)
@retry_db_exception
async def signup_user(user_in: UserCreate, db: Session = Depends(get_db_with_retry)): # <--- Change type hint to Session
    try:
        existing_user = await user_crud.get_by_email(db, email=user_in.email) 
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email already registered"
            )
        
        hashed_password = AuthService.get_password_hash(user_in.password)
        # user_crud.create is now async
        user = await user_crud.create(db, user_in=user_in, hashed_password=hashed_password)
        return user
    except HTTPException as e:
        raise e
    except Exception as e:
        print(f"ERROR: Unhandled exception during signup for email {user_in.email}: {type(e).__name__} - {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected server error occurred during signup. Please try again."
        )

@router.post("/login")
@retry_db_exception
async def login_user(user_in: UserLogin, auth_service: AuthService = Depends(get_auth_service)): # <--- Change type hint to Session
    try:
        user = await auth_service.authenticate_user(user_in.email, user_in.password)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        access_token = auth_service.create_access_token(data={"sub": str(user.id), "name": user.name})
        return {"access_token": access_token, "token_type": "bearer", "user_id": str(user.id)}
    except HTTPException as e:
        raise e
    except Exception as e:
        print(f"ERROR: Unhandled exception during login for email {user_in.email}: {type(e).__name__} - {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected server error occurred during login."
        )

