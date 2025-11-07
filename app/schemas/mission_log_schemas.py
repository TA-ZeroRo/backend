"""MissionLog 관련 Pydantic 스키마"""
from pydantic import BaseModel, ConfigDict
from typing import Optional, Dict, Any
from uuid import UUID
from datetime import datetime
from enum import Enum


class MissionLogBase(BaseModel):
    """MissionLog 기본 스키마"""
    mission_template_id: int
    proof_data: Optional[Dict[str, Any]] = None


class MissionLogStatus(str, Enum):
    """미션 로그 상태"""
    IN_PROGRESS = "IN_PROGRESS"              # 진행 중
    PENDING_VERIFICATION = "PENDING_VERIFICATION"  # 검증 대기
    COMPLETED = "COMPLETED"                  # 완료
    FAILED = "FAILED"                        # 실패


class MissionLogCreate(MissionLogBase):
    """MissionLog 생성 스키마"""
    user_id: UUID


class MissionLogUpdate(BaseModel):
    """MissionLog 업데이트 스키마"""
    status: Optional[MissionLogStatus] = None
    proof_data: Optional[Dict[str, Any]] = None
    completed_at: Optional[datetime] = None


class MissionLogResponse(MissionLogBase):
    """MissionLog 응답 스키마"""
    id: int
    user_id: UUID
    status: MissionLogStatus
    started_at: datetime
    completed_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(
        from_attributes=True,
        json_encoders={
            UUID: lambda v: str(v)
        }
    )
