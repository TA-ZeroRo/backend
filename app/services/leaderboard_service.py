"""Leaderboard Service - 리더보드 관련 비즈니스 로직"""
from typing import Dict, Any, List, Optional
from uuid import UUID
from app.repository.leaderboard_repository import LeaderboardRepository


class LeaderboardService:
    """리더보드 관련 비즈니스 로직을 처리하는 서비스"""

    def __init__(self):
        self.leaderboard_repo = LeaderboardRepository()

    async def get_top_users(self, limit: int = 10) -> Dict[str, List[Dict[str, Any]]]:
        """포인트 기준 상위 사용자 조회"""
        users = await self.leaderboard_repo.get_top_users_by_points(limit)

        # 순위 추가
        for idx, user in enumerate(users, start=1):
            user["rank"] = idx

        return {"leaderboard": users}

    async def get_leaderboard(
        self,
        limit: int = 50,
        user_id: Optional[UUID] = None
    ) -> Dict[str, Any]:
        """리더보드 조회 (상위 limit명 + 내 순위)

        Args:
            limit: 조회할 상위 사용자 수
            user_id: 내 순위를 조회할 사용자 ID (Optional)

        Returns:
            {
                "leaderboard": [...],  # 상위 랭킹 리스트
                "my_rank": {...}       # 내 순위 정보 (user_id가 있을 경우)
            }
        """
        # 상위 랭킹 조회
        users = await self.leaderboard_repo.get_top_users_by_points(limit)

        result = {"leaderboard": users}

        # user_id가 있으면 내 순위도 조회
        if user_id:
            try:
                my_rank = await self.leaderboard_repo.get_user_ranking(str(user_id))
                result["my_rank"] = my_rank
            except Exception:
                # 내 순위 조회 실패 시 None으로 설정
                result["my_rank"] = None
        else:
            result["my_rank"] = None

        return result

    async def get_user_rank(self, user_id: UUID) -> Dict[str, Any] | None:
        """특정 사용자의 정보와 순위 조회"""
        user_data = await self.leaderboard_repo.get_user_ranking(str(user_id))
        return user_data
