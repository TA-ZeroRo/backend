"""Plogging 관련 Pydantic 스키마"""
from pydantic import BaseModel, ConfigDict, Field
from typing import Optional, List, Dict, Any
from uuid import UUID
from datetime import datetime, date
from enum import Enum


class PloggingStatus(str, Enum):
    """플로깅 세션 상태"""
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"


class VerificationStatus(str, Enum):
    """사진 인증 상태"""
    PENDING = "PENDING"
    VERIFIED = "VERIFIED"
    REJECTED = "REJECTED"


# ===== GPS 포인트 =====
class GpsPoint(BaseModel):
    """GPS 포인트"""
    lat: float = Field(..., ge=-90, le=90)
    lng: float = Field(..., ge=-180, le=180)
    timestamp: datetime
    accuracy: Optional[float] = None


# ===== 세션 스키마 =====
class PloggingSessionCreate(BaseModel):
    """플로깅 세션 시작 요청"""
    user_id: UUID
    initial_photo_url: str  # 초기 사진 URL (필수)


class PloggingSessionEnd(BaseModel):
    """플로깅 세션 종료 요청"""
    route_points: List[GpsPoint]


class PloggingSessionResponse(BaseModel):
    """플로깅 세션 응답"""
    id: int
    user_id: UUID
    status: PloggingStatus
    started_at: datetime
    ended_at: Optional[datetime] = None
    duration_minutes: Optional[int] = None
    total_distance_meters: Optional[float] = None
    intensity_level: int = 1
    verification_count: int = 0
    points_earned: int = 0
    created_at: datetime
    initial_photo_url: Optional[str] = None  # 초기 사진 URL

    model_config = ConfigDict(
        from_attributes=True,
        json_encoders={UUID: lambda v: str(v)}
    )


class PloggingSessionWithRoute(PloggingSessionResponse):
    """경로 포함 세션 응답"""
    route_points: Optional[List[GpsPoint]] = None


# ===== 사진 인증 스키마 =====
class PhotoVerificationRequest(BaseModel):
    """사진 인증 요청"""
    image_url: str
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)


class PhotoVerificationResponse(BaseModel):
    """사진 인증 응답"""
    id: int
    session_id: int
    verification_status: VerificationStatus
    ai_confidence: Optional[float] = None
    ai_result: Optional[Dict[str, Any]] = None
    points_earned: int = 0
    verified_at: datetime

    model_config = ConfigDict(from_attributes=True)


class AIVerificationResult(BaseModel):
    """AI 검증 결과"""
    is_valid: bool
    confidence: float = Field(..., ge=0.0, le=1.0)
    detected_items: List[str] = []
    reason: str


class AIComparisonResult(BaseModel):
    """AI 사진 비교 검증 결과 (초기 사진 vs 현재 사진)"""
    is_same_person: bool  # 동일 인물 여부
    trash_increased: bool  # 쓰레기 양 증가 여부
    confidence: float = Field(..., ge=0.0, le=1.0)
    reason: str  # 검증 결과 설명 (한국어)


# ===== 경로 스키마 =====
class RouteSegment(BaseModel):
    """경로 세그먼트 (지도 표시용)"""
    points: List[GpsPoint]
    intensity_level: int
    duration_minutes: int


class CommunityRoute(BaseModel):
    """커뮤니티 경로 (다른 사용자 경로)"""
    session_id: int
    user_id: UUID
    intensity_level: int
    route_points: List[GpsPoint]
    created_at: datetime


class MapRoutesResponse(BaseModel):
    """지도 경로 데이터 응답"""
    routes: List[CommunityRoute]
    total_count: int


# ===== H3 집계 스키마 =====
class H3Aggregation(BaseModel):
    """H3 그리드 집계"""
    h3_index: str
    center_lat: float
    center_lng: float
    total_sessions: int
    total_duration_minutes: int
    avg_intensity: float


class H3MapResponse(BaseModel):
    """H3 지도 데이터 응답"""
    cells: List[H3Aggregation]
    aggregation_date: date


# ===== 통계 스키마 =====
class UserPloggingStats(BaseModel):
    """사용자 플로깅 통계"""
    total_sessions: int = 0
    total_duration_minutes: int = 0
    total_distance_meters: float = 0
    total_verifications: int = 0
    total_points_earned: int = 0
    avg_intensity_level: float = 1.0
