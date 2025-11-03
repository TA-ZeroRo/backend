"""Mission 관련 Pydantic 스키마"""
from pydantic import BaseModel, ConfigDict
from typing import Optional
from uuid import UUID
from datetime import datetime
from enum import Enum


class MissionStatus(str, Enum):
    """미션 상태"""
    PROGRESS = "PROGRESS"          # 진행 중
    VERIFICATION = "VERIFICATION"  # 검증 대기 중
    COMPLETED = "COMPLETED"        # 성공
    FAILED = "FAILED"              # 실패


class MissionResponse(BaseModel):
    """Mission 응답 스키마"""
    id: int
    user_id: UUID
    campaign_id: int
    description: Optional[str] = None
    status: MissionStatus
    started_at: datetime
    completed_at: Optional[datetime] = None

    model_config = ConfigDict(
        from_attributes=True,
        json_encoders={
            UUID: lambda v: str(v)
        }
    )