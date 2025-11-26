"""Recruiting and Chat 관련 Pydantic 스키마"""
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, Dict, Any
from uuid import UUID
from datetime import datetime, date


# ===== RecruitingPost 스키마 =====
class RecruitingPostBase(BaseModel):
    """RecruitingPost 기본 스키마"""
    campaign_id: int
    title: str
    region: str
    city: str
    capacity: int = Field(gt=0, description="최대 참여 인원 (1 이상)")
    start_date: date
    end_date: Optional[date] = None
    min_age: int = Field(ge=0, default=0, description="최소 연령 (0이면 제한 없음)")
    max_age: int = Field(ge=0, default=0, description="최대 연령 (0이면 제한 없음)")


class RecruitingPostCreate(RecruitingPostBase):
    """RecruitingPost 생성 스키마"""
    user_id: UUID


class RecruitingPostUpdate(BaseModel):
    """RecruitingPost 업데이트 스키마"""
    user_id: UUID  # 권한 검증용
    title: Optional[str] = None
    region: Optional[str] = None
    city: Optional[str] = None
    capacity: Optional[int] = Field(None, gt=0)
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    min_age: Optional[int] = Field(None, ge=0)
    max_age: Optional[int] = Field(None, ge=0)
    is_recruiting: Optional[bool] = None


class RecruitingPostResponse(RecruitingPostBase):
    """RecruitingPost 응답 스키마"""
    id: int
    user_id: UUID
    current_members: int
    is_recruiting: bool
    created_at: datetime
    updated_at: datetime
    profiles: Optional[Dict[str, Any]] = None  # user_img, username 포함
    chat_room_id: Optional[int] = None  # 채팅방 ID (있는 경우)
    is_participating: bool = False  # 현재 사용자 참여 여부

    model_config = ConfigDict(
        from_attributes=True,
        json_encoders={
            UUID: lambda v: str(v),
            date: lambda v: v.isoformat(),
            datetime: lambda v: v.isoformat()
        }
    )


class RecruitingPostDelete(BaseModel):
    """RecruitingPost 삭제 스키마"""
    user_id: UUID


# ===== ChatRoom 스키마 =====
class ChatRoomBase(BaseModel):
    """ChatRoom 기본 스키마"""
    recruiting_post_id: int


class ChatRoomCreate(ChatRoomBase):
    """ChatRoom 생성 스키마"""
    pass


class ChatRoomResponse(ChatRoomBase):
    """ChatRoom 응답 스키마"""
    id: int
    created_at: datetime
    participant_count: Optional[int] = 0

    model_config = ConfigDict(
        from_attributes=True,
        json_encoders={
            datetime: lambda v: v.isoformat()
        }
    )


# ===== ChatMessage 스키마 =====
class ChatMessageBase(BaseModel):
    """ChatMessage 기본 스키마"""
    message: str = Field(min_length=1, description="메시지 내용")


class ChatMessageSend(ChatMessageBase):
    """ChatMessage 전송 스키마 (URL에서 room_id를 받는 경우)"""
    user_id: UUID


class ChatMessageCreate(ChatMessageBase):
    """ChatMessage 생성 스키마 (내부용)"""
    user_id: UUID
    chat_room_id: int


class ChatMessageResponse(ChatMessageBase):
    """ChatMessage 응답 스키마"""
    id: int
    chat_room_id: int
    user_id: UUID
    created_at: datetime
    profiles: Optional[Dict[str, Any]] = None  # user_img, username 포함

    model_config = ConfigDict(
        from_attributes=True,
        json_encoders={
            UUID: lambda v: str(v),
            datetime: lambda v: v.isoformat()
        }
    )


# ===== Join 스키마 =====
class JoinRecruitingRequest(BaseModel):
    """리크루팅 참여 요청 스키마"""
    user_id: UUID
