"""Report Endpoint - 보고서 API"""
from fastapi import APIRouter, Path, Query
from uuid import UUID
from typing import List, Optional
from app.services.report_service import ReportService
from app.schemas.report_schemas import MonthlyReportResponse

router = APIRouter()
report_service = ReportService()


@router.get("/{user_id}", response_model=List[MonthlyReportResponse])
async def get_monthly_reports(
    user_id: UUID = Path(..., description="사용자 ID"),
    limit: Optional[int] = Query(None, ge=1, le=24, description="조회할 보고서 개수 (생략 시 가입 월부터 전체)")
):
    """
    월간보고서 목록 조회

    사용자의 월간 활동 내역을 조회합니다.
    (현재 월 포함, 가입 월부터 현재까지)

    **각 보고서 포함 정보:**
    - 참여한 캠페인 목록
    - 완료한 미션 (카테고리별)
    - 포인트 획득 내역 (전달과 비교)
    - 환경 TMI
    - 첫 열람 시 20포인트 자동 지급

    **Parameters:**
    - user_id: 사용자 UUID
    - limit: 조회할 보고서 개수 (생략 시 가입 월부터 전체, 최대 24개월)

    **Returns:**
    - 보고서 목록 (최근순, 현재 월부터 가입 월까지)
    """
    return await report_service.get_monthly_reports(user_id=user_id, limit=limit)
