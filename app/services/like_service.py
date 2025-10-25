"""Like Service - 좋아요 관련 비즈니스 로직"""
from fastapi import HTTPException
from uuid import UUID
from typing import Dict, Any, List
from app.repository.like_repository import LikeRepository
from app.repository.community_repository import CommunityRepository
from app.schemas.like_schemas import LikeCreate


class LikeService:
    """좋아요 관련 비즈니스 로직을 처리하는 서비스"""

    def __init__(self):
        self.like_repo = LikeRepository()
        self.community_repo = CommunityRepository()

    async def create_like(self, user_id: UUID, post_id: int) -> Dict[str, Any]:
        """좋아요 생성"""
        # 이미 좋아요를 눌렀는지 확인
        existing_like = await self.like_repo.get_like_by_user_and_post(user_id, post_id)
        if existing_like:
            raise HTTPException(status_code=409, detail="이미 좋아요를 눌렀습니다.")

        # 좋아요 생성
        like_data = {
            "user_id": str(user_id),
            "post_id": post_id
        }

        created_like = await self.like_repo.create_like(like_data)
        if not created_like:
            raise HTTPException(status_code=500, detail="좋아요 생성에 실패했습니다.")

        # 게시글의 좋아요 수 증가
        await self.community_repo.increment_likes(post_id)

        return {"message": "좋아요가 성공적으로 추가되었습니다.", "like": created_like}

    async def delete_like(self, user_id: UUID, post_id: int) -> Dict[str, str]:
        """좋아요 삭제"""
        # 좋아요 찾기
        existing_like = await self.like_repo.get_like_by_user_and_post(user_id, post_id)
        if not existing_like:
            raise HTTPException(status_code=404, detail="좋아요를 찾을 수 없습니다.")

        # 좋아요 삭제
        success = await self.like_repo.delete_like(existing_like["id"])
        if not success:
            raise HTTPException(status_code=500, detail="좋아요 삭제에 실패했습니다.")

        # 게시글의 좋아요 수 감소
        await self.community_repo.decrement_likes(post_id)

        return {"message": "좋아요가 성공적으로 삭제되었습니다."}

    async def get_likes_by_user(self, user_id: UUID) -> Dict[str, List[Dict[str, Any]]]:
        """사용자의 좋아요 목록 조회"""
        likes = await self.like_repo.get_likes_by_user_id(user_id)
        return {"likes": likes}

    async def get_likes_by_post(self, post_id: int) -> Dict[str, List[Dict[str, Any]]]:
        """게시글의 좋아요 목록 조회"""
        likes = await self.like_repo.get_likes_by_post_id(post_id)
        return {"likes": likes}

    async def check_user_liked_post(self, user_id: UUID, post_id: int) -> Dict[str, bool]:
        """사용자가 게시글에 좋아요를 눌렀는지 확인"""
        liked = await self.like_repo.check_like_exists(user_id, post_id)
        return {"liked": liked}

    async def get_liked_post_ids(self, user_id: UUID, post_ids: List[int]) -> Dict[str, List[int]]:
        """사용자가 좋아요를 누른 게시글 ID 목록 조회"""
        if not post_ids:
            raise HTTPException(status_code=400, detail="post_ids는 필수입니다.")

        # 모든 좋아요 가져오기
        all_likes = await self.like_repo.get_likes_by_user_id(user_id)

        # post_ids에 포함된 것만 필터링
        liked_post_ids = [
            like["post_id"] for like in all_likes
            if like["post_id"] in post_ids
        ]

        return {"liked_post_ids": liked_post_ids}

    async def toggle_like(self, user_id: UUID, post_id: int) -> Dict[str, Any]:
        """
        인스타그램처럼 좋아요 토글 기능을 제공합니다.
        - 좋아요가 없으면 → 추가
        - 좋아요가 있으면 → 삭제

        Returns:
            {
                "action": "added" | "removed",
                "likes_count": int,
                "is_liked": bool
            }
        """
        # 현재 좋아요 상태 확인
        existing_like = await self.like_repo.get_like_by_user_and_post(user_id, post_id)

        if existing_like:
            # 좋아요가 있는 경우 → 삭제
            success = await self.like_repo.delete_like(existing_like["id"])
            if not success:
                raise HTTPException(status_code=500, detail="좋아요 삭제에 실패했습니다.")

            # 게시글의 좋아요 수 감소
            await self.community_repo.decrement_likes(post_id)

            # 최종 좋아요 수 조회
            post = await self.community_repo.get_post_by_id(post_id)
            likes_count = post.get("likes_count", 0) if post else 0

            return {
                "action": "removed",
                "likes_count": likes_count,
                "is_liked": False
            }
        else:
            # 좋아요가 없는 경우 → 추가
            like_data = {
                "user_id": str(user_id),
                "post_id": post_id
            }

            created_like = await self.like_repo.create_like(like_data)
            if not created_like:
                raise HTTPException(status_code=500, detail="좋아요 추가에 실패했습니다.")

            # 게시글의 좋아요 수 증가
            await self.community_repo.increment_likes(post_id)

            # 최종 좋아요 수 조회
            post = await self.community_repo.get_post_by_id(post_id)
            likes_count = post.get("likes_count", 0) if post else 0

            return {
                "action": "added",
                "likes_count": likes_count,
                "is_liked": True
            }
