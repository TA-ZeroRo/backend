"""Like 관련 Pydantic 스키마"""
from pydantic import BaseModel, ConfigDict
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

    model_config = ConfigDict(
        from_attributes=True,
        json_encoders={
            UUID: lambda v: str(v)
        }
    )
