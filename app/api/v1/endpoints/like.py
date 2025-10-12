from fastapi import APIRouter, HTTPException
from uuid import UUID
from typing import List
from app.services.like_service import LikeService

router = APIRouter()
like_service = LikeService()

@router.post("/like")
async def create_like_endpoint(post_id: int, user_id: UUID):
    """
    특정 게시글에 좋아요를 추가합니다.
    """
    try:
        return await like_service.create_like(user_id, post_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/like")
async def delete_like_endpoint(post_id: int, user_id: UUID):
    """
    특정 게시글에서 사용자의 좋아요를 삭제합니다.
    """
    try:
        return await like_service.delete_like(user_id, post_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/like")
async def get_liked_post_ids_endpoint(user_id: UUID, post_ids: List[int]):
    """
    user_id가 post_ids 중 어떤 게시글에 좋아요를 눌렀는지 반환합니다.
    """
    try:
        return await like_service.get_liked_post_ids(user_id, post_ids)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/toggle")
async def toggle_like_endpoint(post_id: int, user_id: UUID):
    """
    인스타그램처럼 좋아요 토글 기능을 제공합니다.
    - 좋아요가 없으면 추가
    - 좋아요가 있으면 삭제

    Response:
    {
        "action": "added" | "removed",
        "likes_count": int,
        "is_liked": bool
    }
    """
    try:
        return await like_service.toggle_like(user_id, post_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
