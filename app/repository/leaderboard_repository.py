"""Leaderboard Repository"""
from typing import List, Dict, Any
from app.repository.base_repository import BaseRepository


class LeaderboardRepository(BaseRepository):
    """리더보드 관련 데이터베이스 작업을 처리하는 Repository"""

    async def get_top_users_by_points(self, limit: int = 10) -> List[Dict[str, Any]]:
        """포인트 기준 상위 사용자 조회"""
        response = (
            self.supabase
            .table("profiles")
            .select("id, username, user_img, total_points, continuous_days")
            .order("total_points", desc=True)
            .order("continuous_days", desc=True)
            .limit(limit)
            .execute()
        )
        data = response.data if response.data else []
        # Add sequential rank based on current ordering
        for index, item in enumerate(data, start=1):
            item["rank"] = index
        return data

    async def get_user_ranking(self, user_id: str) -> Dict[str, Any] | None:
        """특정 사용자의 정보와 순위 조회"""
        # 해당 유저의 정보 가져오기
        user_response = (
            self.supabase
            .table("profiles")
            .select("id, username, user_img, total_points")
            .eq("id", user_id)
            .single()
            .execute()
        )

        if not user_response.data:
            return None

        user_data = user_response.data
        user_points = user_data["total_points"]

        # 해당 유저보다 포인트가 높은 유저 수 세기
        ranking_response = (
            self.supabase
            .table("profiles")
            .select("id", count="exact")  # type: ignore
            .gt("total_points", user_points)
            .execute()
        )

        rank = ranking_response.count + 1 if ranking_response.count is not None else 1
        user_data["rank"] = rank

        return user_data
