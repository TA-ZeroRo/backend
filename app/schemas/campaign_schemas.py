"""Campaign 관련 Pydantic 스키마"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import date, datetime
from enum import Enum


# ===== Campaign Enums =====
class CampaignCategory(str, Enum):
    """캠페인 카테고리"""
    RECYCLING = "재활용"              # 재활용/분리수거
    TRANSPORTATION = "대중교통"        # 대중교통/자전거
    ENERGY = "에너지절약"             # 에너지 절약
    ZERO_WASTE = "제로웨이스트"        # 제로웨이스트/다회용기
    CONSERVATION = "자연보호"          # 자연보호/환경정화
    EDUCATION = "교육"                # 교육/세미나
    OTHER = "기타"                    # 기타


class CampaignStatus(str, Enum):
    """캠페인 상태"""
    EXPECT = "EXPECT"    # 예정
    ACTIVE = "ACTIVE"    # 활성 (진행중)
    EXPIRED = "EXPIRED"  # 기간 만료


class SubmissionType(str, Enum):
    """캠페인 제출 방식"""
    WEBVIEW_ASSISTED = "WEBVIEW_ASSISTED"  # 웹뷰 어시스트
    DIRECT_API = "DIRECT_API"              # 직접 API 연동
    MANUAL = "MANUAL"                      # 수동 안내


class CampaignType(str, Enum):
    """캠페인 유형"""
    ONLINE = "ONLINE"    # 온라인 캠페인 (위치 무관)
    OFFLINE = "OFFLINE"  # 오프라인 캠페인 (특정 장소)


class CampaignSource(str, Enum):
    """캠페인 출처"""
    ZERORO = "ZERORO"      # 제로로 자체 캠페인 (앱 내 미션 참여 가능)
    EXTERNAL = "EXTERNAL"  # 외부 캠페인 (웹뷰 연결만 제공)


# ===== Offline Campaign Location 스키마 =====
class OfflineCampaignLocationBase(BaseModel):
    """오프라인 캠페인 위치 정보 기본 스키마"""
    location_lat: float = Field(..., description="캠페인 장소 위도")
    location_lng: float = Field(..., description="캠페인 장소 경도")
    location_radius: int = Field(100, description="허용 반경 (미터)")
    location_address: Optional[str] = Field(None, description="사람이 읽을 수 있는 주소")


class OfflineCampaignLocationResponse(OfflineCampaignLocationBase):
    """오프라인 캠페인 위치 정보 응답 스키마"""
    id: int

    class Config:
        from_attributes = True


class OfflineCampaignLocationCreate(OfflineCampaignLocationBase):
    """오프라인 캠페인 위치 정보 생성 스키마"""
    pass


# ===== Campaign 응답 스키마 =====
class CampaignResponse(BaseModel):
    """Campaign 응답 스키마"""
    id: int
    title: str
    description: Optional[str] = None
    host_organizer: str
    campaign_url: str
    image_url: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    region: Optional[str] = None
    category: Optional[CampaignCategory] = None
    status: CampaignStatus
    submission_type: Optional[SubmissionType] = None
    campaign_type: CampaignType = Field(CampaignType.ONLINE, description="캠페인 유형")
    campaign_source: CampaignSource = Field(CampaignSource.EXTERNAL, description="캠페인 출처")
    updated_at: datetime

    # 오프라인 캠페인인 경우 위치 정보 포함
    location: Optional[OfflineCampaignLocationResponse] = Field(None, description="오프라인 캠페인 위치 정보")

    class Config:
        from_attributes = True
