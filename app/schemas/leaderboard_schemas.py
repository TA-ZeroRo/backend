"""Leaderboard 관련 Pydantic 스키마"""
from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from uuid import UUID


class LeaderboardUserResponse(BaseModel):
    """리더보드 사용자 응답 스키마"""
    id: UUID
    username: Optional[str]
    user_img: Optional[str]
    total_points: int
    rank: Optional[int] = None

    model_config = ConfigDict(
        from_attributes=True,
        json_encoders={
            UUID: lambda v: str(v)
        }
    )


class LeaderboardResponse(BaseModel):
    """리더보드 전체 응답 스키마 (상위 랭킹 + 내 순위)"""
    leaderboard: List[LeaderboardUserResponse]
    my_rank: Optional[LeaderboardUserResponse] = None

    model_config = ConfigDict(
        from_attributes=True,
        json_encoders={
            UUID: lambda v: str(v)
        }
    )
