"""Community (Post) 관련 Pydantic 스키마"""
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from uuid import UUID
from datetime import datetime


# ===== Post 스키마 =====
class PostBase(BaseModel):
    """Post 기본 스키마"""
    title: str
    content: str
    image_url: Optional[str] = None


class PostCreate(PostBase):
    """Post 생성 스키마"""
    user_id: UUID


class PostUpdate(BaseModel):
    """Post 업데이트 스키마"""
    title: Optional[str] = None
    content: Optional[str] = None
    image_url: Optional[str] = None


class PostResponse(PostBase):
    """Post 응답 스키마"""
    id: int
    user_id: UUID
    likes_count: int = 0
    comments_count: int = 0  # DB 스키마와 일치
    created_at: datetime
    profiles: Optional[Dict[str, Any]] = None  # user_img, username 포함

    class Config:
        from_attributes = True

