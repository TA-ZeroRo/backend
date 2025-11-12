"""RPA Execution Request/Response Schemas"""
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field


class RPAExecuteRequest(BaseModel):
    """RPA 실행 요청 스키마"""

    campaign_id: int = Field(..., description="Campaign ID")
    submission_data: Dict[str, Any] = Field(
        ...,
        description="제출할 데이터 (field_mapping에 정의된 키 사용)",
        example={
            "title": "미션 제목",
            "content": "미션 내용",
            "photo": "/path/to/image.jpg"
        }
    )
    credentials: Dict[str, str] = Field(
        ...,
        description="로그인 인증 정보",
        example={
            "username": "test_user",
            "password": "test_password"
        }
    )

    class Config:
        json_schema_extra = {
            "example": {
                "campaign_id": 3,
                "submission_data": {
                    "title": "친환경 미션 완료",
                    "content": "텀블러 사용으로 일회용 컵 줄이기 실천했습니다.",
                    "photo": "/uploads/mission_photo.jpg"
                },
                "credentials": {
                    "username": "testuser",
                    "password": "testpass123"
                }
            }
        }


class RPAExecuteResponse(BaseModel):
    """RPA 실행 결과 스키마"""

    success: bool = Field(..., description="실행 성공 여부")
    message: Optional[str] = Field(None, description="성공 메시지")
    error: Optional[str] = Field(None, description="에러 메시지")
    execution_time: Optional[float] = Field(None, description="실행 시간 (초)")
    campaign_id: int = Field(..., description="실행된 Campaign ID")

    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "message": "Successfully submitted",
                "error": None,
                "execution_time": 12.5,
                "campaign_id": 3
            }
        }
