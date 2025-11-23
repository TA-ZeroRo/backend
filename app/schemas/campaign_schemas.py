"""Campaign 관련 Pydantic 스키마"""
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
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
    RPA_FORM_SUBMIT = "RPA_FORM_SUBMIT"  # RPA 폼 자동 제출
    DIRECT_API = "DIRECT_API"            # 직접 API 연동
    MANUAL_GUIDE = "MANUAL_GUIDE"        # 수동 안내
    WEBVIEW_ASSISTED = "WEBVIEW_ASSISTED"  # 웹뷰 어시스트


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
    updated_at: datetime

    # RPA 하이브리드 구조 (로그인 공유 + 폼 개별)
    rpa_site_config_id: Optional[int] = Field(None, description="RPA 사이트 설정 ID (로그인 공유)")
    rpa_form_url: Optional[str] = Field(None, description="RPA 폼 제출 URL (Campaign별)")
    rpa_form_config: Optional[Dict[str, Any]] = Field(None, description="RPA 폼 셀렉터 설정 (Campaign별)")
    rpa_field_mapping: Optional[Dict[str, str]] = Field(None, description="submission_data → 폼 셀렉터 매핑")
    rpa_form_selector_strategies: Optional[Dict[str, Any]] = Field(None, description="Self-Healing 폼 셀렉터 전략")

    class Config:
        from_attributes = True
