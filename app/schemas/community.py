from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from uuid import UUID


# ===== Post 스키마 =====
class PostBase(BaseModel):
    title: str
    content: str


class PostCreate(PostBase):
    image_url: Optional[str] = None


class PostUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    image_url: Optional[str] = None


class PostResponse(PostBase):
    id: int
    user_id: UUID
    image_url: Optional[str] = None
    likes_count: int = 0
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ===== Comment 스키마 =====
class CommentBase(BaseModel):
    content: str


class CommentCreate(CommentBase):
    post_id: int


class CommentUpdate(BaseModel):
    content: Optional[str] = None


class CommentResponse(CommentBase):
    id: int
    post_id: int
    user_id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
