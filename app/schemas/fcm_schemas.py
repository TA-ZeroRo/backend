"""FCM 관련 Pydantic 스키마"""
from pydantic import BaseModel, Field
from typing import Optional, Literal
from uuid import UUID


class FcmTokenRegister(BaseModel):
    """FCM 토큰 등록 요청"""
    user_id: UUID = Field(..., description="사용자 ID")
    fcm_token: str = Field(..., description="FCM 토큰")
    platform: Literal["android", "ios"] = Field(..., description="플랫폼 (android/ios)")


class FcmTokenDelete(BaseModel):
    """FCM 토큰 삭제 요청"""
    user_id: UUID = Field(..., description="사용자 ID")
    fcm_token: str = Field(..., description="삭제할 FCM 토큰")


class FcmTokenResponse(BaseModel):
    """FCM 토큰 응답"""
    id: int
    user_id: str
    fcm_token: str
    platform: str
    created_at: str
    updated_at: str


class ChatPushNotification(BaseModel):
    """채팅 푸시 알림 데이터"""
    chat_room_id: int = Field(..., description="채팅방 ID")
    sender_id: str = Field(..., description="발신자 ID")
    sender_name: str = Field(..., description="발신자 이름")
    message: str = Field(..., description="메시지 내용")
    recruiting_post_id: Optional[int] = Field(None, description="리크루팅 게시글 ID")
    recruiting_title: Optional[str] = Field(None, description="리크루팅 제목")
