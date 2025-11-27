"""Campaign Repository"""
from typing import List, Dict, Any, Optional
from app.repository.base_repository import BaseRepository


class CampaignRepository(BaseRepository):
    """캠페인 관련 데이터베이스 작업을 처리하는 Repository"""

    TABLE_NAME = "campaigns"
    LOCATION_TABLE = "offline_campaign_locations"

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
        # campaigns 테이블에서 offline_campaign_locations를 LEFT JOIN으로 조회
        query = self.supabase.table(self.TABLE_NAME).select(
            "*, offline_campaign_locations(id, location_lat, location_lng, location_radius, location_address)"
        )

        # 필터링 적용
        if region:
            query = query.ilike("region", f"%{region}%")

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
        response = self.supabase.table(self.TABLE_NAME)\
            .select("*, offline_campaign_locations(id, location_lat, location_lng, location_radius, location_address)")\
            .eq("id", campaign_id)\
            .execute()

        if not response.data:
            return None

        campaigns = self._process_campaign_locations(response.data)
        return campaigns[0] if campaigns else None

    def _process_campaign_locations(self, campaigns: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        조회 결과를 처리하여 location 객체로 변환

        Parameters:
        - campaigns: 조회한 캠페인 목록

        Returns:
        - location 필드가 정리된 캠페인 목록
        """
        processed = []
        for campaign in campaigns:
            # Supabase가 반환하는 중첩된 offline_campaign_locations를 location으로 변환
            location_data = campaign.pop("offline_campaign_locations", None)

            # location_data가 리스트인 경우 첫 번째 요소 사용 (1:1 관계)
            if isinstance(location_data, list):
                location_data = location_data[0] if location_data else None

            campaign["location"] = location_data
            processed.append(campaign)

        return processed
