"""Report Service - 보고서 관련 비즈니스 로직"""
from fastapi import HTTPException
from uuid import UUID
from datetime import date, datetime
from typing import Dict, Any
from calendar import monthrange

from app.repository.report_repository import ReportRepository
from app.repository.user_repository import UserRepository
from app.schemas.report_schemas import (
    MonthlyReportResponse,
    UserInfo,
    Period,
    CampaignsInfo,
    Campaign,
    MissionsInfo,
    MissionCategory,
    PointsInfo,
    TMI,
    Reward
)


class ReportService:
    """보고서 관련 비즈니스 로직을 처리하는 서비스"""

    FIRST_VIEW_REWARD_POINTS = 20  # 첫 열람 시 지급 포인트

    def __init__(self):
        self.report_repo = ReportRepository()
        self.user_repo = UserRepository()

    async def get_monthly_reports(
        self,
        user_id: UUID,
        limit: int | None = None
    ) -> list[MonthlyReportResponse]:
        """
        여러 월간보고서 조회 (최근순)

        Parameters:
        - user_id: 사용자 ID
        - limit: 조회할 보고서 개수 (None이면 가입 월부터 전체)

        Returns:
        - list[MonthlyReportResponse]: 보고서 목록 (최근순)
        """
        # 사용자 정보 조회 (가입 날짜 확인)
        user_data = await self.user_repo.get_user_by_id(user_id)
        if not user_data:
            raise HTTPException(status_code=404, detail="사용자를 찾을 수 없습니다.")

        # 가입 날짜 파싱
        created_at_str = user_data.get("created_at")
        if created_at_str:
            if isinstance(created_at_str, str):
                created_at = datetime.fromisoformat(created_at_str.replace('Z', '+00:00'))
            else:
                created_at = created_at_str
            signup_year = created_at.year
            signup_month = created_at.month
        else:
            # created_at이 없으면 1년 전부터로 설정
            signup_year = date.today().year - 1
            signup_month = date.today().month

        reports = []
        today = date.today()

        # 현재 월부터 시작 (진행 중인 월 포함)
        current_year = today.year
        current_month = today.month

        # limit이 없으면 가입 월부터 전체 조회
        months_since_signup = (current_year - signup_year) * 12 + (current_month - signup_month) + 1
        max_months = limit if limit is not None else months_since_signup

        # 이전 달부터 역순으로 조회
        for i in range(max_months):
            # i개월 전 계산
            target_year = current_year
            target_month = current_month - i

            # 월이 0 이하로 내려가면 작년으로 이동
            while target_month <= 0:
                target_month += 12
                target_year -= 1

            # 가입 월보다 이전이면 중단
            if target_year < signup_year or (target_year == signup_year and target_month < signup_month):
                break

            try:
                report = await self.get_monthly_report(
                    user_id=user_id,
                    year=target_year,
                    month=target_month
                )
                reports.append(report)
            except HTTPException:
                # 해당 월에 데이터가 없으면 스킵
                continue

        return reports

    async def get_latest_monthly_report(self, user_id: UUID) -> MonthlyReportResponse:
        """
        가장 최근 보고서 조회

        Parameters:
        - user_id: 사용자 ID

        Returns:
        - MonthlyReportResponse: 이전 달 보고서 데이터
        """
        # 사용자 정보 조회 (가입일 확인)
        user_data = await self.user_repo.get_user_by_id(user_id)
        if not user_data:
            raise HTTPException(status_code=404, detail="사용자를 찾을 수 없습니다.")

        # 사용자 가입일
        created_at = user_data.get("created_at")
        if not created_at:
            raise HTTPException(status_code=500, detail="사용자 가입일 정보가 없습니다.")

        # created_at이 문자열인 경우 datetime으로 변환
        if isinstance(created_at, str):
            created_at = datetime.fromisoformat(created_at.replace("Z", "+00:00"))

        user_join_date = created_at.date()

        # 현재 날짜 기준 이전 달 계산
        today = date.today()

        if today.month == 1:
            # 1월인 경우 작년 12월
            previous_year = today.year - 1
            previous_month = 12
        else:
            # 그 외는 이번 년도의 이전 달
            previous_year = today.year
            previous_month = today.month - 1

        # 이전 달의 마지막 날짜
        _, last_day = monthrange(previous_year, previous_month)
        previous_month_end = date(previous_year, previous_month, last_day)

        # 사용자가 이전 달 이후에 가입했다면 보고서 없음
        if user_join_date > previous_month_end:
            raise HTTPException(
                status_code=404,
                detail="아직 생성된 보고서가 없습니다. 가입 후 한 달이 지나면 보고서를 확인할 수 있습니다."
            )

        # 이전 달 보고서 조회
        return await self.get_monthly_report(
            user_id=user_id,
            year=previous_year,
            month=previous_month
        )

    async def get_monthly_report(
        self,
        user_id: UUID,
        year: int,
        month: int
    ) -> MonthlyReportResponse:
        """
        보고서 조회

        Parameters:
        - user_id: 사용자 ID
        - year: 연도
        - month: 월 (1-12)

        Returns:
        - MonthlyReportResponse: 보고서 데이터
        """
        # 월 유효성 검증
        if not (1 <= month <= 12):
            raise HTTPException(status_code=400, detail="월은 1-12 사이의 값이어야 합니다.")

        # 1. 사용자 정보 조회
        user_data = await self.user_repo.get_user_by_id(user_id)
        if not user_data:
            raise HTTPException(status_code=404, detail="사용자를 찾을 수 없습니다.")

        user_info = UserInfo(
            id=user_data["id"],
            username=user_data["username"]
        )

        # 2. 해당 월의 기간 계산
        start_date = date(year, month, 1)
        _, last_day = monthrange(year, month)
        end_date = date(year, month, last_day)

        period = Period(start_date=start_date, end_date=end_date)

        # 3. 캠페인 정보 조회
        campaigns_data = await self.report_repo.get_user_campaigns_in_period(
            user_id=user_id,
            start_date=start_date,
            end_date=end_date
        )

        campaign_list = [
            Campaign(
                id=camp["id"],
                title=camp["title"],
                description=camp.get("description")
            )
            for camp in campaigns_data
        ]

        campaigns_info = CampaignsInfo(
            list=campaign_list,
            count=len(campaign_list)
        )

        # 4. 미션 완료 정보 조회 (카테고리별)
        missions_data = await self.report_repo.get_completed_missions_by_category(
            user_id=user_id,
            start_date=start_date,
            end_date=end_date
        )

        mission_categories = [
            MissionCategory(category=item["category"], count=item["count"])
            for item in missions_data
        ]

        total_completed = sum(item["count"] for item in missions_data)

        missions_info = MissionsInfo(
            completed_by_category=mission_categories,
            total_completed=total_completed
        )

        # 5. 포인트 정보 조회 (이번 달, 전달, 차이)
        current_month_points = await self.report_repo.get_user_points_in_month(
            user_id=user_id,
            year=year,
            month=month
        )

        # 전달 계산
        if month == 1:
            prev_year = year - 1
            prev_month = 12
        else:
            prev_year = year
            prev_month = month - 1

        previous_month_points = await self.report_repo.get_user_points_in_month(
            user_id=user_id,
            year=prev_year,
            month=prev_month
        )

        points_info = PointsInfo(
            current_month=current_month_points,
            previous_month=previous_month_points,
            difference=current_month_points - previous_month_points
        )

        # 6. 환경 TMI 조회
        tmi_content = await self.report_repo.get_environmental_tip()
        if not tmi_content:
            tmi_content = "환경을 보호하는 작은 실천이 큰 변화를 만듭니다!"

        tmi = TMI(content=tmi_content)

        # 7. 첫 열람 여부 확인 및 포인트 지급
        is_first_view = not await self.report_repo.check_report_viewed(
            user_id=user_id,
            year=year,
            month=month
        )

        points_earned = 0
        if is_first_view:
            # 첫 열람이므로 포인트 지급
            points_earned = self.FIRST_VIEW_REWARD_POINTS

            # 1. 보고서 조회 기록 먼저 저장 (중복 방지)
            view_record = await self.report_repo.record_report_view(
                user_id=user_id,
                year=year,
                month=month
            )
            if not view_record:
                raise HTTPException(
                    status_code=500,
                    detail="보고서 조회 기록 저장에 실패했습니다."
                )

            # 2. 포인트 로그 추가
            point_data = {
                "user_id": str(user_id),
                "point": points_earned
            }
            point_log = await self.report_repo.create("point_log", point_data)
            if not point_log:
                raise HTTPException(
                    status_code=500,
                    detail="포인트 로그 생성에 실패했습니다."
                )

            # 3. 사용자 total_points 업데이트
            new_total_points = user_data.get("total_points", 0) + points_earned
            updated_user = await self.user_repo.update_user(
                user_id=user_id,
                user_data={"total_points": new_total_points}
            )
            if not updated_user:
                raise HTTPException(
                    status_code=500,
                    detail="사용자 포인트 업데이트에 실패했습니다."
                )

        reward = Reward(
            is_first_view=is_first_view,
            points_earned=points_earned
        )

        # 8. 최종 응답 생성
        return MonthlyReportResponse(
            user=user_info,
            period=period,
            campaigns=campaigns_info,
            missions=missions_info,
            points=points_info,
            tmi=tmi,
            reward=reward
        )
