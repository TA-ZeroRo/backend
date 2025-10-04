from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from uuid import UUID


class PointLogBase(BaseModel):
    point: int
    reason: Optional[str] = None


class PointLogCreate(PointLogBase):
    pass


class PointLogResponse(PointLogBase):
    id: int
    user_id: UUID
    created_at: datetime

    class Config:
        from_attributes = True
