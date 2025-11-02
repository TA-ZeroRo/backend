"""Mission Service - 미션 관련 비즈니스 로직"""
from typing import Dict, Any
from uuid import UUID
from app.repository.mission_repository import MissionRepository


class MissionService:
    """미션 관련 비즈니스 로직을 처리하는 서비스"""

    def __init__(self):
        self.mission_repo = MissionRepository()

    async def get_missions_by_user(self, user_id: UUID) -> Dict[str, Any]:
        """사용자의 미션을 campaign_id별로 그룹화하여 조회"""
        missions = await self.mission_repo.get_missions_by_user_id(user_id)

        # campaign_id별로 그룹화
        missions_by_campaign = {}
        for mission in missions:
            campaign_id = str(mission["campaign_id"])
            if campaign_id not in missions_by_campaign:
                missions_by_campaign[campaign_id] = []
            missions_by_campaign[campaign_id].append(mission)

        return {"missions_by_campaign": missions_by_campaign}