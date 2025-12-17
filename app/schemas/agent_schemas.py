"""Agent Chat Schemas - AI 에이전트 대화 관련 스키마"""
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List, Dict, Any
from uuid import UUID


class ChatMessage(BaseModel):
    """대화 메시지 (사용자 또는 AI)"""
    role: str = Field(..., description="메시지 역할: 'user' 또는 'assistant'")
    content: str = Field(..., description="메시지 내용")


class ChatRequest(BaseModel):
    """AI 에이전트 대화 요청"""
    user_id: UUID = Field(..., description="사용자 ID")
    message: str = Field(..., description="사용자 메시지")
    selected_character: Optional[str] = Field(
        default="earth_zeroro",
        description="선택된 캐릭터 ID (earth_zeroro: 지구 제로로, dust_zeroro: 먼지 제로로)"
    )
    selected_personality: Optional[str] = Field(
        default="friendly",
        description="선택된 성격 ID (friendly, playful, researcher, coach, elegant)"
    )

    model_config = ConfigDict(
        from_attributes=True,
        json_encoders={
            UUID: lambda v: str(v)
        }
    )


class FunctionCallInfo(BaseModel):
    """AI가 호출한 Tool 정보"""
    name: str = Field(..., description="호출된 Tool 이름")
    args: Dict[str, Any] = Field(..., description="Tool 인자")


class ChatResponse(BaseModel):
    """AI 에이전트 대화 응답"""
    message: str = Field(..., description="AI 응답 메시지")
