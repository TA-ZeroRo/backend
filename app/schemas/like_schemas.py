"""Like 관련 Pydantic 스키마"""
from pydantic import BaseModel
from uuid import UUID
from datetime import datetime


class LikeCreate(BaseModel):
    """Like 생성 스키마"""
    user_id: UUID
    post_id: int


class LikeResponse(BaseModel):
    """Like 응답 스키마"""
    id: int
    user_id: UUID
    post_id: int
    created_at: datetime

    class Config:
        from_attributes = True
