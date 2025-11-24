"""Campaign Repository"""
from typing import List, Dict, Any, Optional
from app.repository.base_repository import BaseRepository


class CampaignRepository(BaseRepository):
    """캠페인 관련 데이터베이스 작업을 처리하는 Repository"""

    TABLE_NAME = "campaigns"
    VIEW_NAME = "campaigns_with_location"  # View 사용

    async def get_all_campaigns(
        self,
        region: Optional[str] = None,
        category: Optional[str] = None,
        status: Optional[str] = None,
        campaign_type: Optional[str] = None,
        offset: int = 0,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """
        캠페인 목록 조회 (필터링 + 페이지네이션)

        Parameters:
        - region: 지역 필터 (예: "서울특별시", "경기도")
        - category: 카테고리 필터 (ENUM 값)
        - status: 상태 필터 (ENUM 값, 기본: ACTIVE만 조회)
        - campaign_type: 캠페인 유형 필터 (ONLINE/OFFLINE)
        - offset: 페이지네이션 시작 인덱스
        - limit: 페이지당 조회 개수

        Returns:
        - 캠페인 목록 (location 정보 포함)
        """
        # View 사용 (자동으로 location 정보 JOIN됨)
        query = self.supabase.table(self.VIEW_NAME).select("*")

        # 필터링 적용
        if region:
            query = query.eq("region", region)

        if category:
            query = query.eq("category", category)

        if status:
            query = query.eq("status", status)
        else:
            # 기본값: ACTIVE 상태만 조회
            query = query.eq("status", "ACTIVE")

        if campaign_type:
            query = query.eq("campaign_type", campaign_type)

        # 정렬 및 페이지네이션
        response = (
            query
            .order("updated_at", desc=True)  # 최신 업데이트순
            .range(offset, offset + limit - 1)
            .execute()
        )

        return self._process_campaign_locations(response.data) if response.data else []

    async def get_campaign_by_id(self, campaign_id: int) -> Optional[Dict[str, Any]]:
        """
        캠페인 ID로 단일 캠페인 조회 (location 정보 포함)

        Parameters:
        - campaign_id: 캠페인 ID

        Returns:
        - 캠페인 정보 (location 포함) 또는 None
        """
        # View 사용
        response = self.supabase.table(self.VIEW_NAME)\
            .select("*")\
            .eq("id", campaign_id)\
            .execute()

        if not response.data:
            return None

        campaigns = self._process_campaign_locations(response.data)
        return campaigns[0] if campaigns else None

    def _process_campaign_locations(self, campaigns: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        View 결과를 처리하여 location 객체로 그룹화

        Parameters:
        - campaigns: View에서 조회한 캠페인 목록 (평평한 구조)

        Returns:
        - location 필드가 중첩된 캠페인 목록
        """
        processed = []
        for campaign in campaigns:
            # location 관련 필드들을 별도 객체로 분리
            location_fields = [
                "location_id", "location_lat", "location_lng",
                "location_radius", "location_address",
                "daily_start_time", "daily_end_time"
            ]

            # location 필드가 모두 None이면 location 객체 자체를 None으로
            if all(campaign.get(field) is None for field in location_fields):
                campaign["location"] = None
            else:
                # location 객체 생성
                campaign["location"] = {
                    "id": campaign.pop("location_id", None),
                    "location_lat": campaign.pop("location_lat", None),
                    "location_lng": campaign.pop("location_lng", None),
                    "location_radius": campaign.pop("location_radius", None),
                    "location_address": campaign.pop("location_address", None),
                    "daily_start_time": campaign.pop("daily_start_time", None),
                    "daily_end_time": campaign.pop("daily_end_time", None),
                }

            # 이미 pop한 필드들 제거 (남아있으면)
            for field in location_fields:
                campaign.pop(field, None)

            processed.append(campaign)

        return processed
