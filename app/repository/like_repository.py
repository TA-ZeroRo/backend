"""Like Repository"""
from typing import Optional, List, Dict, Any
from uuid import UUID
from app.repository.base_repository import BaseRepository


class LikeRepository(BaseRepository):
    """좋아요 관련 데이터베이스 작업을 처리하는 Repository"""

    TABLE_NAME = "likes"

    async def get_like_by_id(self, like_id: int) -> Optional[Dict[str, Any]]:
        """좋아요 ID로 좋아요 정보 조회"""
        return await self.find_by_id(self.TABLE_NAME, str(like_id))

    async def get_like_by_user_and_post(self, user_id: UUID, post_id: int) -> Optional[Dict[str, Any]]:
        """사용자 ID와 게시글 ID로 좋아요 조회"""
        response = (
            self.supabase
            .table(self.TABLE_NAME)
            .select("*")
            .eq("user_id", str(user_id))
            .eq("post_id", post_id)
            .execute()
        )
        if response.data and len(response.data) > 0:
            return response.data[0]
        return None

    async def get_likes_by_user_id(self, user_id: UUID) -> List[Dict[str, Any]]:
        """사용자 ID로 좋아요 목록 조회"""
        response = (
            self.supabase
            .table(self.TABLE_NAME)
            .select("*")
            .eq("user_id", str(user_id))
            .execute()
        )
        return response.data if response.data else []

    async def get_likes_by_post_id(self, post_id: int) -> List[Dict[str, Any]]:
        """게시글 ID로 좋아요 목록 조회"""
        response = (
            self.supabase
            .table(self.TABLE_NAME)
            .select("*")
            .eq("post_id", post_id)
            .execute()
        )
        return response.data if response.data else []

    async def create_like(self, like_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """새로운 좋아요 생성"""
        return await self.create(self.TABLE_NAME, like_data)

    async def delete_like(self, like_id: int) -> bool:
        """좋아요 삭제"""
        return await self.delete(self.TABLE_NAME, str(like_id))

    async def check_like_exists(self, user_id: UUID, post_id: int) -> bool:
        """좋아요 존재 여부 확인"""
        like = await self.get_like_by_user_and_post(user_id, post_id)
        return like is not None

    async def get_liked_post_ids_filtered(self, user_id: UUID, post_ids: List[int]) -> List[int]:
        """사용자가 좋아요를 누른 게시글 ID 목록 (DB 레벨 필터링)"""
        if not post_ids:
            return []

        response = (
            self.supabase
            .table(self.TABLE_NAME)
            .select("post_id")
            .eq("user_id", str(user_id))
            .in_("post_id", post_ids)
            .execute()
        )
        return [item["post_id"] for item in response.data] if response.data else []
