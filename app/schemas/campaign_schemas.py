"""Campaign 관련 Pydantic 스키마"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import date, datetime
from enum import Enum


# ===== Campaign Enums =====
class CampaignCategory(str, Enum):
    """캠페인 카테고리"""
    RECYCLING = "RECYCLING"           # 재활용/분리수거
    TRANSPORTATION = "TRANSPORTATION"  # 대중교통/자전거
    ENERGY = "ENERGY"                 # 에너지 절약
    ZERO_WASTE = "ZERO_WASTE"         # 제로웨이스트/다회용기
    CONSERVATION = "CONSERVATION"     # 자연보호/환경정화
    EDUCATION = "EDUCATION"           # 교육/세미나
    OTHER = "OTHER"                   # 기타


class CampaignStatus(str, Enum):
    """캠페인 상태"""
    EXPECT = "EXPECT"    # 예정
    ACTIVE = "ACTIVE"    # 활성 (진행중)
    EXPIRED = "EXPIRED"  # 기간 만료


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
    updated_at: datetime

    class Config:
        from_attributes = True
