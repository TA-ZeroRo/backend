from fastapi import APIRouter, HTTPException
from typing import Optional, List, Dict
from app.services.community_service import CommunityService
from app.schemas.community_schemas import (
    PostCreate, PostUpdate, PostResponse, PostDelete,
    CommentCreate, CommentUpdate, CommentResponse, CommentDelete
)

router = APIRouter()
community_service = CommunityService()

# -------------------------
# --- START: 게시글 API ---
# -------------------------
@router.get("/posts", response_model=List[PostResponse])
async def get_community_posts(offset: int, user_id: Optional[str] = None):
    """
    커뮤니티 게시글 목록을 가져옵니다.

    Parameters:
    - offset (int): 페이지네이션을 위한 시작 인덱스 (필수)
    - user_id (str, optional): 특정 사용자의 게시글만 필터링하고 싶을 때 사용
    """
    return await community_service.get_posts(offset=offset, user_id=user_id)

@router.get("/posts/{post_id}", response_model=PostResponse)
async def get_single_post(post_id: int):
    """
    특정 게시글의 상세 정보를 가져옵니다.
    """
    return await community_service.get_single_post(post_id)

@router.post("/posts", response_model=PostResponse, status_code=201)
async def create_community_post(post_data: PostCreate):
    """
    새로운 커뮤니티 게시글을 생성합니다.
    """
    return await community_service.create_post(post_data)

@router.put("/posts/{post_id}", response_model=PostResponse)
async def update_community_post(post_id: int, post_data: PostUpdate):
    """
    커뮤니티 게시글을 수정합니다.
    """
    return await community_service.update_post(post_id, post_data)

@router.delete("/posts/{post_id}")
async def delete_community_post(post_id: int, delete_data: PostDelete):
    """
    커뮤니티 게시글을 삭제합니다.
    """
    return await community_service.delete_post(post_id, delete_data)
# -----------------------
# --- END: 게시글 API ---
# -----------------------

# -----------------------
# --- START: 댓글 API ---
# -----------------------
@router.get("/posts/{post_id}/comments", response_model=List[CommentResponse])
async def get_post_comments(post_id: int):
    """
    특정 게시글의 댓글 목록을 가져옵니다.
    """
    return await community_service.get_comments(post_id)

@router.post("/posts/{post_id}/comments", response_model=CommentResponse, status_code=201)
async def create_post_comment(post_id: int, comment_data: CommentCreate):
    """
    특정 게시글에 새로운 댓글을 생성합니다.
    """
    return await community_service.create_comment(post_id, comment_data)

@router.put("/posts/{post_id}/comments/{comment_id}", response_model=CommentResponse)
async def update_post_comment(post_id: int, comment_id: int, comment_data: CommentUpdate):
    """
    댓글을 수정합니다.
    """
    return await community_service.update_comment(post_id, comment_id, comment_data)

@router.delete("/posts/{post_id}/comments/{comment_id}")
async def delete_post_comment(post_id: int, comment_id: int, delete_data: CommentDelete):
    """
    댓글을 삭제합니다.
    """
    return await community_service.delete_comment(post_id, comment_id, delete_data)

# ---------------------
# --- END: 댓글 API ---
# ---------------------