"""Offline Campaign Location Repository"""
from typing import Optional
from app.repository.base_repository import BaseRepository


class OfflineLocationRepository(BaseRepository):
    """오프라인 캠페인 위치 정보 Repository"""

    def __init__(self):
        super().__init__()
        self.table_name = "offline_campaign_locations"

    def get_by_campaign_id(self, campaign_id: int) -> Optional[dict]:
        """
        특정 캠페인의 위치 정보 조회

        Args:
            campaign_id: 캠페인 ID

        Returns:
            위치 정보 또는 None
        """
        response = self.supabase.table(self.table_name)\
            .select("*")\
            .eq("campaign_id", campaign_id)\
            .execute()

        return response.data[0] if response.data else None

    def create_location(self, campaign_id: int, location_data: dict) -> dict:
        """
        오프라인 캠페인 위치 정보 생성

        Args:
            campaign_id: 캠페인 ID
            location_data: 위치 정보 (lat, lng, radius, address)

        Returns:
            생성된 위치 정보
        """
        data = {
            "campaign_id": campaign_id,
            **location_data
        }
        response = self.supabase.table(self.table_name)\
            .insert(data)\
            .execute()

        return response.data[0]

    def update_location(self, campaign_id: int, location_data: dict) -> dict:
        """
        오프라인 캠페인 위치 정보 수정

        Args:
            campaign_id: 캠페인 ID
            location_data: 수정할 위치 정보

        Returns:
            수정된 위치 정보
        """
        response = self.supabase.table(self.table_name)\
            .update(location_data)\
            .eq("campaign_id", campaign_id)\
            .execute()

        return response.data[0]

    def delete_location(self, campaign_id: int) -> bool:
        """
        오프라인 캠페인 위치 정보 삭제

        Args:
            campaign_id: 캠페인 ID

        Returns:
            삭제 성공 여부
        """
        response = self.supabase.table(self.table_name)\
            .delete()\
            .eq("campaign_id", campaign_id)\
            .execute()

        return len(response.data) > 0
