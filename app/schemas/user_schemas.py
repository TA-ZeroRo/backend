"""User 관련 Pydantic 스키마"""
from pydantic import BaseModel, Field
from typing import Optional, List
from uuid import UUID
from datetime import datetime


class UserBase(BaseModel):
    """User 기본 스키마"""
    username: Optional[str] = None
    user_img: Optional[str] = None
    total_points: Optional[int] = 0
    continuous_days: Optional[int] = 0
    region: Optional[str] = None
    characters: Optional[List[str]] = None
    last_active_at: Optional[datetime] = None


class UserCreate(UserBase):
    """User 생성 스키마"""
    id: UUID
    username: str  # 필수로 유지


class UserUpdate(BaseModel):
    """User 업데이트 스키마"""
    username: Optional[str] = None
    user_img: Optional[str] = None
    total_points: Optional[int] = None
    region: Optional[str] = None
    characters: Optional[List[str]] = None
    last_active_at: Optional[datetime] = None


class UserResponse(UserBase):
    """User 응답 스키마"""
    id: UUID
    continuous_days: int = 0
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True
