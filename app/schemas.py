from pydantic import BaseModel, EmailStr
from typing import Optional, List

# User Schemas
class UserBase(BaseModel):
    email: EmailStr

class UserCreate(UserBase):
    password: str

class UserResponse(UserBase):
    id: int
    role: str
    is_verified: bool

    class Config:
        orm_mode = True

# File Schemas
class FileBase(BaseModel):
    filename: str
    file_path: str

class FileResponse(FileBase):
    id: int
    uploaded_by: int
    uploaded_at: str

    class Config:
        orm_mode = True
