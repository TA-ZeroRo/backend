from pydantic import BaseModel
from datetime import datetime
from uuid import UUID


class LikeBase(BaseModel):
    post_id: int


class LikeCreate(LikeBase):
    pass


class LikeResponse(LikeBase):
    id: int
    user_id: UUID
    created_at: datetime

    class Config:
        from_attributes = True
