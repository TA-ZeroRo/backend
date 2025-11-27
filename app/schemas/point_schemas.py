"""Point 관련 Pydantic 스키마"""
from pydantic import BaseModel, Field, ConfigDict
from typing import List
from datetime import date as date_type
from uuid import UUID


class PointTrendDataPoint(BaseModel):
    """포인트 추이 데이터 포인트 (일별)"""
    date: date_type = Field(..., description="날짜 (YYYY-MM-DD)")
    total_points: int = Field(..., description="해당 날짜의 누적 총 포인트")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "date": "2025-01-20",
                "total_points": 1250
            }
        }
    )


class PointTrendResponse(BaseModel):
    """포인트 추이 응답 스키마"""
    user_id: UUID = Field(..., description="사용자 ID")
    days: int = Field(..., description="조회 기간 (일)")
    data: List[PointTrendDataPoint] = Field(..., description="일별 포인트 데이터")

    model_config = ConfigDict(
        from_attributes=True,
        json_encoders={
            UUID: lambda v: str(v)
        },
        json_schema_extra={
            "example": {
                "user_id": "550e8400-e29b-41d4-a716-446655440000",
                "days": 7,
                "data": [
                    {"date": "2025-01-14", "total_points": 1000},
                    {"date": "2025-01-15", "total_points": 1050},
                    {"date": "2025-01-16", "total_points": 1100},
                    {"date": "2025-01-17", "total_points": 1150},
                    {"date": "2025-01-18", "total_points": 1180},
                    {"date": "2025-01-19", "total_points": 1230},
                    {"date": "2025-01-20", "total_points": 1250},
                ]
            }
        }
    )


class PointLogCreate(BaseModel):
    """포인트 로그 생성 스키마"""
    user_id: UUID = Field(..., description="사용자 ID")
    point: int = Field(..., description="포인트 (양수: 획득, 음수: 사용)")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "user_id": "550e8400-e29b-41d4-a716-446655440000",
                "point": 100
            }
        }
    )


class PointLogResponse(BaseModel):
    """포인트 로그 응답 스키마"""
    id: int = Field(..., description="로그 ID")
    user_id: UUID = Field(..., description="사용자 ID")
    point: int = Field(..., description="포인트")
    created_at: str = Field(..., description="생성 일시")

    model_config = ConfigDict(
        from_attributes=True,
        json_encoders={
            UUID: lambda v: str(v)
        }
    )
