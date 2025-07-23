# backend/app/schemas/user_schemas.py
from pydantic import BaseModel, EmailStr, Field
from uuid import UUID
from datetime import datetime

# Shared properties
class UserBase(BaseModel):
    email: EmailStr
    name: str | None = None

# Properties to receive via API on creation (signup)
class UserCreate(UserBase):
    password: str = Field(min_length=8)

# Properties to receive via API on login
class UserLogin(BaseModel):
    email: EmailStr
    password: str

# Properties to return via API (response model)
class UserInDB(UserBase):
    id: UUID
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True # For SQLAlchemy ORM compatibility
        from_attributes = True # Pydantic v2 equivalent of orm_mode