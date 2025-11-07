"""MissionTemplate 관련 Pydantic 스키마"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from enum import Enum


class VerificationType(str, Enum):
    """미션 검증 타입"""
    IMAGE = "IMAGE"              # 사진 인증
    QUIZ = "QUIZ"                # 퀴즈
    TEXT_REVIEW = "TEXT_REVIEW"  # 소감문
    RPA_ACTION = "RPA_ACTION"    # RPA 자동 검증


class MissionTemplateBase(BaseModel):
    """MissionTemplate 기본 스키마"""
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    order: int = Field(default=0, ge=0)
    verification_type: VerificationType
    reward_points: int = Field(default=0, ge=0)


class MissionTemplateCreate(MissionTemplateBase):
    """MissionTemplate 생성 스키마"""
    campaign_id: int


class MissionTemplateUpdate(BaseModel):
    """MissionTemplate 업데이트 스키마"""
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    order: Optional[int] = Field(None, ge=0)
    verification_type: Optional[VerificationType] = None
    reward_points: Optional[int] = Field(None, ge=0)


class MissionTemplateResponse(MissionTemplateBase):
    """MissionTemplate 응답 스키마"""
    id: int
    campaign_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
