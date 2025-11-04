"""Report 관련 Pydantic 스키마"""
from pydantic import BaseModel, ConfigDict
from typing import List, Optional
from uuid import UUID
from datetime import date


class UserInfo(BaseModel):
    """사용자 기본 정보"""
    id: UUID
    username: str


class Period(BaseModel):
    """보고서 기간"""
    start_date: date
    end_date: date


class Campaign(BaseModel):
    """캠페인 정보"""
    id: int
    title: str
    description: Optional[str] = None  # 캠페인 설명 (없을 수도 있음)


class CampaignsInfo(BaseModel):
    """캠페인 정보"""
    list: List[Campaign]
    count: int


class MissionCategory(BaseModel):
    """카테고리별 미션 완료 정보"""
    category: str
    count: int


class MissionsInfo(BaseModel):
    """미션 완료 정보"""
    completed_by_category: List[MissionCategory]
    total_completed: int


class PointsInfo(BaseModel):
    """포인트 정보"""
    current_month: int
    previous_month: int
    difference: int


class TMI(BaseModel):
    """환경 TMI"""
    content: str


class Reward(BaseModel):
    """보고서 열람 보상"""
    is_first_view: bool
    points_earned: int


class MonthlyReportResponse(BaseModel):
    """월간 보고서 응답 스키마"""
    user: UserInfo
    period: Period
    campaigns: CampaignsInfo
    missions: MissionsInfo
    points: PointsInfo
    tmi: TMI
    reward: Reward

    model_config = ConfigDict(
        from_attributes=True,
        json_encoders={
            UUID: lambda v: str(v),
            date: lambda v: v.isoformat()
        }
    )
