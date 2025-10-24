"""Community Repository"""
from typing import Optional, List, Dict, Any
from uuid import UUID
from app.repository.base_repository import BaseRepository


class CommunityRepository(BaseRepository):
    """커뮤니티(게시글) 관련 데이터베이스 작업을 처리하는 Repository"""

    POST_TABLE = "posts"

    # ===== 게시글 관련 메서드 =====
    async def get_post_by_id(self, post_id: int) -> Optional[Dict[str, Any]]:
        """게시글 ID로 게시글 조회 (프로필 정보 포함)"""
        response = (
            self.supabase
            .table(self.POST_TABLE)
            .select("*, profiles!posts_user_id_fkey(user_img, username)")
            .eq("id", post_id)
            .single()
            .execute()
        )
        return response.data if response.data else None

    async def get_all_posts(self) -> List[Dict[str, Any]]:
        """모든 게시글 조회 (프로필 정보 포함)"""
        response = (
            self.supabase
            .table(self.POST_TABLE)
            .select("*, profiles!posts_user_id_fkey(user_img, username)")
            .order("created_at", desc=True)
            .execute()
        )
        return response.data if response.data else []

    async def get_posts_paginated(
        self,
        offset: int,
        limit: int = 10,
        user_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """페이지네이션 및 필터링이 적용된 게시글 조회 (프로필 정보 포함)"""
        query = (
            self.supabase
            .table(self.POST_TABLE)
            .select("*, profiles!posts_user_id_fkey(user_img, username)")
            .order("created_at", desc=True)
        )

        # 선택적 user_id 필터링
        if user_id:
            query = query.eq("user_id", user_id)

        # 페이지네이션 적용 (Supabase range는 inclusive)
        response = query.range(offset, offset + limit - 1).execute()
        return response.data if response.data else []

    async def create_post(self, post_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """새로운 게시글 생성"""
        # 1단계: INSERT
        insert_response = (
            self.supabase
            .table(self.POST_TABLE)
            .insert(post_data)
            .execute()
        )

        if not insert_response.data or len(insert_response.data) == 0:
            return None

        # 생성된 게시글의 ID 추출
        created_post_id = insert_response.data[0]["id"]

        # 2단계: 프로필 정보와 함께 조회
        return await self.get_post_by_id(created_post_id)

    async def update_post(self, post_id: int, post_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """게시글 업데이트"""
        response = (
            self.supabase
            .table(self.POST_TABLE)
            .update(post_data)
            .eq("id", post_id)
            .execute()
        )

        if response.data and len(response.data) > 0:
            return await self.get_post_by_id(post_id)
        return None

    async def delete_post(self, post_id: int) -> bool:
        """게시글 삭제"""
        return await self.delete(self.POST_TABLE, str(post_id))

    async def increment_likes(self, post_id: int) -> bool:
        """게시글 좋아요 수 증가"""
        response = (
            self.supabase
            .rpc("increment_likes", {"post_id": post_id})
            .execute()
        )
        return response.data is not None

    async def decrement_likes(self, post_id: int) -> bool:
        """게시글 좋아요 수 감소"""
        response = (
            self.supabase
            .rpc("decrement_likes", {"post_id": post_id})
            .execute()
        )
        return response.data is not None

    async def increment_likes_and_get_count(self, post_id: int) -> int:
        """게시글 좋아요 수 증가 후 최신 likes_count 반환"""
        # RPC 함수 호출
        await self.increment_likes(post_id)

        # 업데이트된 게시글 조회
        post = await self.get_post_by_id(post_id)
        return post.get("likes_count", 0) if post else 0

    async def decrement_likes_and_get_count(self, post_id: int) -> int:
        """게시글 좋아요 수 감소 후 최신 likes_count 반환"""
        # RPC 함수 호출
        await self.decrement_likes(post_id)

        # 업데이트된 게시글 조회
        post = await self.get_post_by_id(post_id)
        return post.get("likes_count", 0) if post else 0
