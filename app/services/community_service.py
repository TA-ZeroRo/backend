"""Community Service - 커뮤니티(게시글) 관련 비즈니스 로직"""
from fastapi import HTTPException
from typing import Dict, Any, List, Optional
from app.repository.community_repository import CommunityRepository
from app.schemas.community_schemas import PostCreate, PostUpdate


class CommunityService:
    """커뮤니티 관련 비즈니스 로직을 처리하는 서비스"""

    def __init__(self):
        self.community_repo = CommunityRepository()

    # ===== 게시글 관련 메서드 =====
    async def get_posts(self, offset: int, user_id: Optional[str] = None) -> Dict[str, List[Dict[str, Any]]]:
        """게시글 목록 조회 (페이지네이션)"""
        if offset is None:
            raise HTTPException(status_code=400, detail="offset는 필수입니다.")

        # Repository 계층에서 페이지네이션 및 필터링 처리
        limit = 10
        posts = await self.community_repo.get_posts_paginated(
            offset=offset,
            limit=limit,
            user_id=user_id
        )

        return {"posts": posts}

    async def create_post(self, post_data: PostCreate) -> Dict[str, Any]:
        """새로운 게시글 생성"""
        # 게시글 데이터 준비
        insert_data = {
            "title": post_data.title,
            "user_id": str(post_data.user_id),
            "content": post_data.content,
            "likes_count": 0
        }

        # 선택적 필드 추가
        if post_data.image_url:
            insert_data["image_url"] = post_data.image_url

        created_post = await self.community_repo.create_post(insert_data)
        if not created_post:
            raise HTTPException(status_code=500, detail="게시글 생성에 실패했습니다.")

        return {"post": created_post}

    async def update_post(self, post_id: int, post_data: PostUpdate) -> Dict[str, Any]:
        """게시글 업데이트"""
        # 업데이트할 데이터만 추출 (None이 아닌 값만)
        update_data = {k: v for k, v in post_data.model_dump().items() if v is not None}

        if not update_data:
            raise HTTPException(status_code=400, detail="업데이트할 데이터가 없습니다.")

        updated_post = await self.community_repo.update_post(post_id, update_data)
        if not updated_post:
            raise HTTPException(status_code=500, detail="게시글 수정에 실패했습니다.")

        return {"post": updated_post}

    async def delete_post(self, post_id: int) -> Dict[str, str]:
        """게시글 삭제"""
        success = await self.community_repo.delete_post(post_id)
        if not success:
            raise HTTPException(status_code=500, detail="게시글 삭제에 실패했습니다.")

        return {"message": "게시글이 성공적으로 삭제되었습니다."}
