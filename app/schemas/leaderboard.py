from pydantic import BaseModel
from datetime import datetime
from uuid import UUID


class LeaderboardResponse(BaseModel):
    user_id: UUID
    total_point: int
    rank: int
    updated_at: datetime

    class Config:
        from_attributes = True
