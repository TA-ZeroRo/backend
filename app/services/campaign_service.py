"""Campaign Service - 캠페인 관련 비즈니스 로직"""
from typing import Dict, Any, List, Optional
from app.repository.campaign_repository import CampaignRepository


class CampaignService:
    """캠페인 관련 비즈니스 로직을 처리하는 서비스"""

    def __init__(self):
        self.campaign_repo = CampaignRepository()

    async def get_campaigns(
        self,
        region: Optional[str] = None,
        category: Optional[str] = None,
        status: Optional[str] = None,
        offset: int = 0,
        limit: int = 20
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        캠페인 목록 조회

        Parameters:
        - region: 지역 필터
        - category: 카테고리 필터
        - status: 상태 필터 (기본: ACTIVE)
        - offset: 페이지네이션 오프셋
        - limit: 페이지당 조회 개수 (기본: 20)

        Returns:
        - {"campaigns": [...]}
        """
        campaigns = await self.campaign_repo.get_all_campaigns(
            region=region,
            category=category,
            status=status,
            offset=offset,
            limit=limit
        )

        return {"campaigns": campaigns}
