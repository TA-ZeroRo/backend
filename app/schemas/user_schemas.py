"""User 관련 Pydantic 스키마"""
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from uuid import UUID
from datetime import datetime


class UserBase(BaseModel):
    """User 기본 스키마"""
    user_img: Optional[str] = None
    total_points: Optional[int] = 0
    continuous_days: Optional[int] = 0
    characters: Optional[List[str]] = []
    personalities: Optional[List[str]] = []
    gacha_tickets: Optional[int] = 0
    last_active_at: Optional[datetime] = None


class UserCreate(UserBase):
    """User 생성 스키마 (id, username, region 필수)"""
    id: UUID
    username: str
    region: str


class UserUpdate(BaseModel):
    """User 업데이트 스키마 (continuous_days는 시스템 자동 관리)"""
    username: Optional[str] = None
    user_img: Optional[str] = None
    total_points: Optional[int] = None
    region: Optional[str] = None
    characters: Optional[List[str]] = None
    personalities: Optional[List[str]] = None
    gacha_tickets: Optional[int] = None
    last_active_at: Optional[datetime] = None


class UserResponse(UserBase):
    """User 응답 스키마 (UUID는 JSON 직렬화 시 자동으로 문자열로 변환)"""
    id: UUID
    username: str
    region: str
    continuous_days: int = 0
    created_at: Optional[datetime] = None

    model_config = ConfigDict(
        from_attributes=True,
        json_encoders={
            UUID: lambda v: str(v)
        }
    )
