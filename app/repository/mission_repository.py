"""Mission Repository"""
from typing import List, Dict, Any
from uuid import UUID
from app.repository.base_repository import BaseRepository


class MissionRepository(BaseRepository):
    """미션 관련 데이터베이스 작업을 처리하는 Repository"""

    TABLE_NAME = "mission"

    async def get_missions_by_user_id(self, user_id: UUID) -> List[Dict[str, Any]]:
        """사용자 ID로 미션 목록 조회"""
        response = (
            self.supabase
            .table(self.TABLE_NAME)
            .select("*")
            .eq("user_id", str(user_id))
            .order("started_at", desc=True)
            .execute()
        )
        return response.data if response.data else []
