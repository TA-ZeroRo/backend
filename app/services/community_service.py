"""Community Service - 커뮤니티(게시글, 댓글) 관련 비즈니스 로직"""
from fastapi import HTTPException
from typing import Dict, Any, List, Optional
from uuid import UUID
from app.repository.community_repository import CommunityRepository
from app.schemas.community_schemas import PostCreate, PostUpdate, PostDelete, CommentCreate, CommentUpdate, CommentDelete


class CommunityService:
    """커뮤니티 관련 비즈니스 로직을 처리하는 서비스"""

    def __init__(self):
        self.community_repo = CommunityRepository()

    # ===== 게시글 관련 메서드 =====
    async def get_posts(self, offset: int, user_id: Optional[str] = None) -> List[Dict[str, Any]]:
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

        return posts

    async def get_single_post(self, post_id: int) -> Dict[str, Any]:
        """
        특정 게시글의 상세 정보를 가져옵니다.
        """
        # 게시글 조회 (DB에 comments_count 포함)
        post = await self.community_repo.get_post_by_id(post_id)
        if not post:
            raise HTTPException(status_code=404, detail="해당 게시글을 찾을 수 없습니다.")

        return post

    async def create_post(self, post_data: PostCreate) -> Dict[str, Any]:
        """새로운 게시글 생성"""
        # 게시글 데이터 준비
        insert_data = {
            "title": post_data.title,
            "user_id": str(post_data.user_id),
            "content": post_data.content,
            "likes_count": 0,
            "comments_count": 0
        }

        # 선택적 필드 추가
        if post_data.image_url:
            insert_data["image_url"] = post_data.image_url

        created_post = await self.community_repo.create_post(insert_data)
        if not created_post:
            raise HTTPException(status_code=500, detail="게시글 생성에 실패했습니다.")

        return created_post

    async def update_post(self, post_id: int, post_data: PostUpdate) -> Dict[str, Any]:
        """게시글 업데이트 (권한 검증 포함)"""
        # 작성자 권한 검증
        post = await self.community_repo.get_post_by_id(post_id)
        if not post:
            raise HTTPException(status_code=404, detail="해당 게시글을 찾을 수 없습니다.")

        if str(post.get("user_id")) != str(post_data.user_id):
            raise HTTPException(status_code=403, detail="게시글을 수정할 권한이 없습니다.")

        # 업데이트할 데이터만 추출 (None이 아닌 값만, user_id 제외)
        update_data = {k: v for k, v in post_data.model_dump(exclude={"user_id"}).items() if v is not None}

        if not update_data:
            raise HTTPException(status_code=400, detail="업데이트할 데이터가 없습니다.")

        updated_post = await self.community_repo.update_post(post_id, update_data)
        if not updated_post:
            raise HTTPException(status_code=500, detail="게시글 수정에 실패했습니다.")

        return updated_post

    async def delete_post(self, post_id: int, delete_data: PostDelete) -> Dict[str, str]:
        """게시글 삭제 (권한 검증 포함)"""
        # 작성자 권한 검증
        post = await self.community_repo.get_post_by_id(post_id)
        if not post:
            raise HTTPException(status_code=404, detail="해당 게시글을 찾을 수 없습니다.")

        if str(post.get("user_id")) != str(delete_data.user_id):
            raise HTTPException(status_code=403, detail="게시글을 삭제할 권한이 없습니다.")

        success = await self.community_repo.delete_post(post_id)
        if not success:
            raise HTTPException(status_code=500, detail="게시글 삭제에 실패했습니다.")

        return {"message": "게시글이 성공적으로 삭제되었습니다."}

    # ===== 댓글 관련 메서드 =====
    async def get_comments(self, post_id: int) -> List[Dict[str, Any]]:
        """특정 게시글의 댓글 목록 조회"""
        comments = await self.community_repo.get_comments_by_post_id(post_id)
        return comments

    async def create_comment(self, post_id: int, comment_data: CommentCreate) -> Dict[str, Any]:
        """새로운 댓글 생성"""
        insert_data = {
            "post_id": post_id,
            "user_id": str(comment_data.user_id),
            "content": comment_data.content
        }

        created_comment = await self.community_repo.create_comment(insert_data)
        if not created_comment:
            raise HTTPException(status_code=500, detail="댓글 생성에 실패했습니다.")

        return created_comment

    async def update_comment(self, post_id: int, comment_id: int, comment_data: CommentUpdate) -> Dict[str, Any]:
        """댓글 업데이트 (권한 검증 포함)"""
        # 작성자 권한 검증
        comment = await self.community_repo.get_comment_by_id(comment_id)
        if not comment:
            raise HTTPException(status_code=404, detail="해당 댓글을 찾을 수 없습니다.")

        if str(comment.get("user_id")) != str(comment_data.user_id):
            raise HTTPException(status_code=403, detail="댓글을 수정할 권한이 없습니다.")

        update_data = {"content": comment_data.content}

        updated_comment = await self.community_repo.update_comment(comment_id, update_data)
        if not updated_comment:
            raise HTTPException(status_code=500, detail="댓글 수정에 실패했습니다.")

        return updated_comment

    async def delete_comment(self, post_id: int, comment_id: int, delete_data: CommentDelete) -> Dict[str, str]:
        """댓글 삭제 (권한 검증 포함)"""
        # 작성자 권한 검증
        comment = await self.community_repo.get_comment_by_id(comment_id)
        if not comment:
            raise HTTPException(status_code=404, detail="해당 댓글을 찾을 수 없습니다.")

        if str(comment.get("user_id")) != str(delete_data.user_id):
            raise HTTPException(status_code=403, detail="댓글을 삭제할 권한이 없습니다.")

        success = await self.community_repo.delete_comment(comment_id)
        if not success:
            raise HTTPException(status_code=500, detail="댓글 삭제에 실패했습니다.")

        return {"message": "댓글이 성공적으로 삭제되었습니다."}
