from app.core.database import get_db
from app.services.auth_service import AuthService
from fastapi import Depends, Header, HTTPException, status
from tenacity import retry, stop_after_attempt, wait_fixed, retry_if_exception_type
from asyncpg.exceptions import DuplicatePreparedStatementError
from sqlalchemy.orm import Session



# Dependency to extract and verify Bearer token
async def get_current_user_id(authorization: str = Header(None)) -> str:
    """
    Extract and verify the Bearer token from the Authorization header.
    Returns the user_id (sub claim) from the token.
    
    Raises HTTPException if token is missing, invalid, or expired.
    """
    if not authorization:
        print("[AUTH DEBUG] Authorization header missing")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization header missing",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    print(f"[AUTH DEBUG] Authorization header present: {authorization[:50]}...")
    
    # Extract token from "Bearer <token>"
    parts = authorization.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        print(f"[AUTH DEBUG] Invalid format: parts={len(parts)}, first_part='{parts[0] if parts else 'N/A'}'")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization header format. Expected 'Bearer <token>'",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    token = parts[1]
    print(f"[AUTH DEBUG] Token extracted: {token[:50]}...")
    from jose import JWTError
    try:
        user_id = AuthService.verify_token(token)
        print(f"[AUTH DEBUG] Token verification result: user_id={user_id}")
        if not user_id:
            print("[AUTH DEBUG] verify_token returned None")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired token",
                headers={"WWW-Authenticate": "Bearer"},
            )
        print(f"[AUTH DEBUG] Successfully authenticated user: {user_id}")
        return user_id
    except JWTError as e:
        print(f"[AUTH DEBUG] JWTError during verification: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
            
retry_db_exception = retry(
    stop=stop_after_attempt(3),
    wait=wait_fixed(1),
    retry=retry_if_exception_type(DuplicatePreparedStatementError), # Still retry on this error type
    reraise=True
)

get_db_with_retry = retry_db_exception(get_db)

def get_auth_service(db: Session = Depends(get_db_with_retry)) -> AuthService: # <--- Change type hint to Session
    return AuthService(db)

