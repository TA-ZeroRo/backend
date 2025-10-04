from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional
from uuid import UUID


class ProfileBase(BaseModel):
    username: str
    email: EmailStr


class ProfileCreate(ProfileBase):
    user_img: Optional[str] = None


class ProfileUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    user_img: Optional[str] = None


class ProfileResponse(ProfileBase):
    id: UUID
    user_img: Optional[str] = None
    total_point: int = 0
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
