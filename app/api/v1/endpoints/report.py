"""Report Endpoint - 보고서 API"""
from fastapi import APIRouter, Path
from uuid import UUID
from app.services.report_service import ReportService
from app.schemas.report_schemas import MonthlyReportResponse

router = APIRouter()
report_service = ReportService()


@router.get("/{user_id}", response_model=MonthlyReportResponse)
async def get_latest_monthly_report(
    user_id: UUID = Path(..., description="사용자 ID")
):
    """
    최근 보고서 조회

    사용자의 가장 최근 월 활동 내역을 자동으로 조회합니다.
    (현재 날짜 기준 이전 달 보고서)

    - 참여한 캠페인 목록
    - 완료한 미션 (카테고리별)
    - 포인트 획득 내역 (전달과 비교)
    - 환경 TMI
    - 첫 열람 시 20포인트 자동 지급

    **Parameters:**
    - user_id: 사용자 UUID

    **Returns:**
    - 보고서 상세 정보 (이전 달 보고서)
    """
    return await report_service.get_latest_monthly_report(user_id=user_id)
