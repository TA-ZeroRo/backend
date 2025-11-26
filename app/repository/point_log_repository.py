"""Point Log Repository"""
from typing import Optional, Dict, Any, List
from uuid import UUID
from datetime import datetime
from app.repository.base_repository import BaseRepository


class PointLogRepository(BaseRepository):
    """포인트 로그 관련 데이터베이스 작업을 처리하는 Repository"""

    TABLE_NAME = "point_log"

    async def create_point_log(
        self,
        user_id: UUID,
        point: int,
        description: str
    ) -> Optional[Dict[str, Any]]:
        """
        포인트 로그 생성

        Parameters:
        -----------
        user_id : UUID
            사용자 ID
        point : int
            포인트 (양수: 획득, 음수: 사용)
        description : str
            포인트 변동 사유

        Returns:
        --------
        Optional[Dict[str, Any]]
            생성된 포인트 로그
        """
        log_data = {
            "user_id": str(user_id),
            "point": point,
            "description": description,
            "created_at": datetime.now().isoformat()
        }
        return await self.create(self.TABLE_NAME, log_data)

    async def get_logs_by_user(
        self,
        user_id: UUID,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """
        특정 사용자의 포인트 로그 조회

        Parameters:
        -----------
        user_id : UUID
            사용자 ID
        limit : int
            조회할 최대 개수

        Returns:
        --------
        List[Dict[str, Any]]
            포인트 로그 리스트
        """
        response = (
            self.supabase
            .table(self.TABLE_NAME)
            .select("*")
            .eq("user_id", str(user_id))
            .order("created_at", desc=True)
            .limit(limit)
            .execute()
        )
        return response.data if response.data else []

    async def get_log_by_id(self, log_id: int) -> Optional[Dict[str, Any]]:
        """포인트 로그 ID로 조회"""
        return await self.find_by_id(self.TABLE_NAME, log_id)

    async def get_total_points_earned(self, user_id: UUID) -> int:
        """
        사용자가 획득한 총 포인트 (양수만)

        Parameters:
        -----------
        user_id : UUID
            사용자 ID

        Returns:
        --------
        int
            총 획득 포인트
        """
        response = (
            self.supabase
            .table(self.TABLE_NAME)
            .select("point")
            .eq("user_id", str(user_id))
            .gt("point", 0)
            .execute()
        )

        if not response.data:
            return 0

        return sum(log["point"] for log in response.data)

    async def get_total_points_spent(self, user_id: UUID) -> int:
        """
        사용자가 사용한 총 포인트 (음수의 절댓값)

        Parameters:
        -----------
        user_id : UUID
            사용자 ID

        Returns:
        --------
        int
            총 사용 포인트 (양수)
        """
        response = (
            self.supabase
            .table(self.TABLE_NAME)
            .select("point")
            .eq("user_id", str(user_id))
            .lt("point", 0)
            .execute()
        )

        if not response.data:
            return 0

        return abs(sum(log["point"] for log in response.data))
