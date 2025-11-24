"""Mission Log Service - 미션 로그 관련 비즈니스 로직"""
from typing import Dict, Any, List, Optional
from uuid import UUID
from app.repository.mission_log_repository import MissionLogRepository


class MissionLogService:
    """미션 로그 관련 비즈니스 로직을 처리하는 서비스"""

    def __init__(self):
        self.mission_log_repo = MissionLogRepository()

    async def get_mission_logs_by_user(
        self,
        user_id: UUID,
        include_template: bool = True,
        include_campaign: bool = True
    ) -> List[Dict[str, Any]]:
        """
        사용자의 미션 로그 목록 조회

        Parameters:
        - user_id: 사용자 UUID
        - include_template: mission_templates 정보 포함 여부
        - include_campaign: campaigns 정보 포함 여부

        Returns:
        - 미션 로그 목록
        """
        return await self.mission_log_repo.get_by_user_id(
            user_id,
            include_template=include_template,
            include_campaign=include_campaign
        )

    async def get_mission_log_by_id(
        self,
        log_id: int,
        include_template: bool = True,
        include_campaign: bool = True,
        include_user: bool = True
    ) -> Optional[Dict[str, Any]]:
        """
        미션 로그 ID로 단일 로그 조회

        Parameters:
        - log_id: 미션 로그 ID
        - include_template: mission_templates 정보 포함 여부
        - include_campaign: campaigns 정보 포함 여부
        - include_user: 사용자 정보 포함 여부

        Returns:
        - 미션 로그 정보 또는 None
        """
        return await self.mission_log_repo.get_log_by_id(
            log_id,
            include_template=include_template,
            include_campaign=include_campaign,
            include_user=include_user
        )

    async def get_mission_logs_by_template(
        self,
        mission_template_id: int,
        include_user: bool = False
    ) -> List[Dict[str, Any]]:
        """
        미션 템플릿 ID로 미션 로그 목록 조회

        Parameters:
        - mission_template_id: 미션 템플릿 ID
        - include_user: 사용자 정보 포함 여부

        Returns:
        - 미션 로그 목록
        """
        return await self.mission_log_repo.get_by_template_id(
            mission_template_id,
            include_user=include_user
        )

    async def get_mission_logs_by_user_and_status(
        self,
        user_id: UUID,
        status: str,
        include_template: bool = True,
        include_campaign: bool = True
    ) -> List[Dict[str, Any]]:
        """
        사용자 ID와 상태로 미션 로그 목록 조회

        Parameters:
        - user_id: 사용자 UUID
        - status: 미션 상태
        - include_template: mission_templates 정보 포함 여부
        - include_campaign: campaigns 정보 포함 여부

        Returns:
        - 미션 로그 목록
        """
        return await self.mission_log_repo.get_by_user_and_status(
            user_id,
            status,
            include_template=include_template,
            include_campaign=include_campaign
        )

    async def get_mission_logs_by_campaign(
        self,
        campaign_id: int,
        user_id: Optional[UUID] = None,
        include_template: bool = True,
        include_user: bool = False
    ) -> List[Dict[str, Any]]:
        """
        캠페인 ID로 미션 로그 목록 조회

        Parameters:
        - campaign_id: 캠페인 ID
        - user_id: 특정 사용자로 필터링 (선택사항)
        - include_template: mission_templates 정보 포함 여부
        - include_user: 사용자 정보 포함 여부

        Returns:
        - 미션 로그 목록
        """
        return await self.mission_log_repo.get_by_campaign_id(
            campaign_id,
            user_id=user_id,
            include_template=include_template,
            include_user=include_user
        )

    async def get_user_mission_by_template(
        self,
        user_id: UUID,
        mission_template_id: int
    ) -> Optional[Dict[str, Any]]:
        """
        특정 사용자의 특정 미션 템플릿 로그 조회

        Parameters:
        - user_id: 사용자 UUID
        - mission_template_id: 미션 템플릿 ID

        Returns:
        - 미션 로그 정보 또는 None
        """
        return await self.mission_log_repo.get_by_user_and_template(
            user_id,
            mission_template_id
        )