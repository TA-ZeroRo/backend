"""MissionTemplate Repository"""
from typing import List, Dict, Any, Optional
from app.repository.base_repository import BaseRepository


class MissionTemplateRepository(BaseRepository):
    """미션 템플릿 관련 데이터베이스 작업을 처리하는 Repository"""

    TABLE_NAME = "mission_templates"

    async def get_by_campaign_id(self, campaign_id: int) -> List[Dict[str, Any]]:
        """
        캠페인 ID로 미션 템플릿 목록 조회 (순서대로)

        Parameters:
        - campaign_id: 캠페인 ID

        Returns:
        - 미션 템플릿 목록 (order 순서대로)
        """
        response = (
            self.supabase
            .table(self.TABLE_NAME)
            .select("*")
            .eq("campaign_id", campaign_id)
            .order("order", desc=False)
            .execute()
        )
        return response.data if response.data else []

    async def get_template_by_id(self, template_id: int) -> Optional[Dict[str, Any]]:
        """
        미션 템플릿 ID로 단일 템플릿 조회

        Parameters:
        - template_id: 미션 템플릿 ID

        Returns:
        - 미션 템플릿 정보 또는 None
        """
        return await self.find_by_id(self.TABLE_NAME, str(template_id))

    async def create_template(self, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        미션 템플릿 생성

        Parameters:
        - data: 템플릿 데이터

        Returns:
        - 생성된 템플릿 정보
        """
        return await self.create(self.TABLE_NAME, data)

    async def update_template(self, template_id: int, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        미션 템플릿 업데이트

        Parameters:
        - template_id: 미션 템플릿 ID
        - data: 업데이트할 데이터

        Returns:
        - 업데이트된 템플릿 정보
        """
        return await self.update(self.TABLE_NAME, str(template_id), data)

    async def delete_template(self, template_id: int) -> bool:
        """
        미션 템플릿 삭제

        Parameters:
        - template_id: 미션 템플릿 ID

        Returns:
        - 삭제 성공 여부
        """
        return await self.delete(self.TABLE_NAME, str(template_id))
