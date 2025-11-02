"""Report Repository"""
from typing import List, Dict, Any, Optional
from uuid import UUID
from datetime import date
from app.repository.base_repository import BaseRepository


class ReportRepository(BaseRepository):
    """보고서 관련 데이터베이스 작업을 처리하는 Repository"""

    async def get_user_campaigns_in_period(
        self,
        user_id: UUID,
        start_date: date,
        end_date: date
    ) -> List[Dict[str, Any]]:
        """
        특정 기간 동안 사용자가 참여한 캠페인 목록 조회

        Parameters:
        - user_id: 사용자 ID
        - start_date: 시작 날짜
        - end_date: 종료 날짜

        Returns:
        - 캠페인 목록 (id, title, description)
        """
        response = (
            self.supabase
            .table("mission")
            .select("campaign_id, campaigns(id, title, description)")
            .eq("user_id", str(user_id))
            .gte("started_at", start_date.isoformat())
            .lte("started_at", end_date.isoformat())
            .execute()
        )

        # 중복 제거 및 campaigns 데이터 추출
        campaigns_dict = {}
        if response.data:
            for item in response.data:
                if item.get("campaigns"):
                    campaign = item["campaigns"]
                    campaign_id = campaign.get("id")
                    if campaign_id and campaign_id not in campaigns_dict:
                        campaigns_dict[campaign_id] = campaign

        return list(campaigns_dict.values())

    async def get_completed_missions_by_category(
        self,
        user_id: UUID,
        start_date: date,
        end_date: date
    ) -> List[Dict[str, Any]]:
        """
        특정 기간 동안 사용자가 완료한 미션을 카테고리별로 집계

        Parameters:
        - user_id: 사용자 ID
        - start_date: 시작 날짜
        - end_date: 종료 날짜

        Returns:
        - 카테고리별 미션 완료 수 [{"category": "...", "count": n}, ...]
        """
        response = (
            self.supabase
            .table("mission")
            .select("campaigns(category)")
            .eq("user_id", str(user_id))
            .eq("status", "COMPLETED")
            .gte("completed_at", start_date.isoformat())
            .lte("completed_at", end_date.isoformat())
            .execute()
        )

        # 카테고리별로 집계
        category_count: Dict[str, int] = {}
        if response.data:
            for item in response.data:
                if item.get("campaigns"):
                    category = item["campaigns"].get("category")
                    if category:
                        category_count[category] = category_count.get(category, 0) + 1

        # 리스트 형태로 변환
        return [{"category": cat, "count": cnt} for cat, cnt in category_count.items()]

    async def get_user_points_in_month(
        self,
        user_id: UUID,
        year: int,
        month: int
    ) -> int:
        """
        특정 월의 사용자 포인트 획득 총합

        Parameters:
        - user_id: 사용자 ID
        - year: 연도
        - month: 월

        Returns:
        - 해당 월의 총 획득 포인트
        """
        # 해당 월의 시작일과 종료일 계산
        start_date = date(year, month, 1)
        if month == 12:
            end_date = date(year + 1, 1, 1)
        else:
            end_date = date(year, month + 1, 1)

        response = (
            self.supabase
            .table("point_log")
            .select("point")
            .eq("user_id", str(user_id))
            .gte("created_at", start_date.isoformat())
            .lt("created_at", end_date.isoformat())
            .execute()
        )

        # 포인트 합산
        total_points = 0
        if response.data:
            total_points = sum(item.get("point", 0) for item in response.data)

        return total_points

    async def check_report_viewed(
        self,
        user_id: UUID,
        year: int,
        month: int
    ) -> bool:
        """
        사용자가 해당 월의 보고서를 이미 조회했는지 확인

        Parameters:
        - user_id: 사용자 ID
        - year: 연도
        - month: 월

        Returns:
        - True: 이미 조회함, False: 처음 조회
        """
        action_type = f"MONTHLY_REPORT_VIEW_{year}_{month:02d}"
        response = (
            self.supabase
            .table("activity_log")
            .select("id")
            .eq("user_id", str(user_id))
            .eq("action_type", action_type)
            .execute()
        )
        return bool(response.data)

    async def record_report_view(
        self,
        user_id: UUID,
        year: int,
        month: int
    ) -> Optional[Dict[str, Any]]:
        """
        월간 보고서 조회 기록 생성

        Parameters:
        - user_id: 사용자 ID
        - year: 연도
        - month: 월

        Returns:
        - 생성된 기록 또는 None
        """
        action_type = f"MONTHLY_REPORT_VIEW_{year}_{month:02d}"
        data = {
            "user_id": str(user_id),
            "action_type": action_type
        }
        return await self.create("activity_log", data)

    async def get_environmental_tip(self) -> Optional[str]:
        """
        랜덤 환경 TMI 조회

        Returns:
        - 환경 TMI 내용 또는 None
        """
        import random

        # 하드코딩된 환경 TMI 리스트
        tips = [
            "플라스틱 병 1개가 완전히 분해되는 데 약 450년이 걸립니다.",
            "재활용 알루미늄 캔 1개로 절약되는 에너지로 TV를 3시간 시청할 수 있습니다.",
            "종이 1톤을 재활용하면 나무 17그루를 살릴 수 있습니다.",
            "LED 전구는 백열전구보다 75% 적은 에너지를 사용하고 25배 더 오래 사용할 수 있습니다.",
            "대중교통 이용으로 1년에 약 2.6톤의 CO2 배출을 줄일 수 있습니다.",
            "샤워 시간을 1분 줄이면 약 7-10리터의 물을 절약할 수 있습니다.",
            "음식물 쓰레기를 줄이면 전 세계 온실가스 배출의 8%를 감소시킬 수 있습니다.",
            "텀블러 사용으로 1년에 약 500개의 일회용 컵 사용을 줄일 수 있습니다."
        ]

        return random.choice(tips)
