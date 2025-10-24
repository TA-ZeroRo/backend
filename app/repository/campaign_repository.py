"""Campaign Repository"""
from typing import List, Dict, Any, Optional
from app.repository.base_repository import BaseRepository


class CampaignRepository(BaseRepository):
    """캠페인 관련 데이터베이스 작업을 처리하는 Repository"""

    TABLE_NAME = "campaigns"

    async def get_all_campaigns(
        self,
        region: Optional[str] = None,
        category: Optional[str] = None,
        status: Optional[str] = None,
        offset: int = 0,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """
        캠페인 목록 조회 (필터링 + 페이지네이션)

        Parameters:
        - region: 지역 필터 (예: "서울특별시", "경기도")
        - category: 카테고리 필터 (ENUM 값)
        - status: 상태 필터 (ENUM 값, 기본: ACTIVE만 조회)
        - offset: 페이지네이션 시작 인덱스
        - limit: 페이지당 조회 개수

        Returns:
        - 캠페인 목록
        """
        query = self.supabase.table(self.TABLE_NAME).select("*")

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

        # 정렬 및 페이지네이션
        response = (
            query
            .order("updated_at", desc=True)  # 최신 업데이트순
            .range(offset, offset + limit - 1)
            .execute()
        )

        return response.data if response.data else []

    async def get_campaign_by_id(self, campaign_id: int) -> Optional[Dict[str, Any]]:
        """
        캠페인 ID로 단일 캠페인 조회

        Parameters:
        - campaign_id: 캠페인 ID

        Returns:
        - 캠페인 정보 또는 None
        """
        return await self.find_by_id(self.TABLE_NAME, str(campaign_id))
