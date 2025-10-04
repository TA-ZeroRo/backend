"""Character 관련 Pydantic 스키마"""
from pydantic import BaseModel
from typing import Optional
from uuid import UUID
from datetime import datetime


class CharacterBase(BaseModel):
    """Character 기본 스키마"""
    name: Optional[str] = None
    description: Optional[str] = None
    image_url: Optional[str] = None


class CharacterCreate(CharacterBase):
    """Character 생성 스키마"""
    user_id: UUID


class CharacterUpdate(BaseModel):
    """Character 업데이트 스키마"""
    name: Optional[str] = None
    description: Optional[str] = None
    image_url: Optional[str] = None


class CharacterResponse(CharacterBase):
    """Character 응답 스키마"""
    id: int
    user_id: UUID
    created_at: datetime

    class Config:
        from_attributes = True
