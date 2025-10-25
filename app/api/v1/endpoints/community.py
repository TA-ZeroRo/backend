from fastapi import APIRouter, HTTPException
from typing import Optional
from app.services.community_service import CommunityService
from app.schemas.community_schemas import PostCreate, PostUpdate, CommentCreate, CommentUpdate

router = APIRouter()
community_service = CommunityService()

# -------------------------
# --- START: 게시글 API ---
# -------------------------
@router.get("/posts")
async def get_community_posts(offset: int, user_id: Optional[str] = None):
    """
    커뮤니티 게시글 목록을 가져옵니다.

    Parameters:
    - offset (int): 페이지네이션을 위한 시작 인덱스 (필수)
    - user_id (str, optional): 특정 사용자의 게시글만 필터링하고 싶을 때 사용
    """
    try:
        return await community_service.get_posts(offset=offset, user_id=user_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/posts/{post_id}")
async def get_single_post(post_id: int):
    """
    특정 게시글의 상세 정보를 가져옵니다.
    댓글 수를 포함하여 반환합니다.
    """
    try:
        return await community_service.get_single_post(post_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/posts")
async def create_community_post(post_data: PostCreate):
    """
    새로운 커뮤니티 게시글을 생성합니다.
    """
    try:
        return await community_service.create_post(post_data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/posts/{post_id}")
async def update_community_post(post_id: int, post_data: PostUpdate, user_id: str):
    """
    커뮤니티 게시글을 수정합니다.

    Parameters:
    - user_id (str): 수정 권한 검증을 위한 사용자 ID (필수)
    """
    try:
        return await community_service.update_post(post_id, post_data, user_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/posts/{post_id}")
async def delete_community_post(post_id: int, user_id: str):
    """
    커뮤니티 게시글을 삭제합니다.

    Parameters:
    - user_id (str): 삭제 권한 검증을 위한 사용자 ID (필수)
    """
    try:
        return await community_service.delete_post(post_id, user_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
# -----------------------
# --- END: 게시글 API ---
# -----------------------

# -----------------------
# --- START: 댓글 API ---
# -----------------------
@router.get("/posts/{post_id}/comments")
async def get_post_comments(post_id: int):
    """
    특정 게시글의 댓글 목록을 가져옵니다.
    """
    try:
        return await community_service.get_comments(post_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/posts/{post_id}/comments")
async def create_post_comment(post_id: int, comment_data: CommentCreate):
    """
    특정 게시글에 새로운 댓글을 생성합니다.
    """
    try:
        return await community_service.create_comment(post_id, comment_data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/posts/{post_id}/comments/{comment_id}")
async def update_post_comment(post_id: int, comment_id: int, comment_data: str, user_id: str):
    """
    댓글을 수정합니다.

    Parameters:
    - user_id (str): 수정 권한 검증을 위한 사용자 ID (필수)
    """
    try:
        return await community_service.update_comment(post_id, comment_id, comment_data, user_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/posts/{post_id}/comments/{comment_id}")
async def delete_post_comment(post_id: int, comment_id: int, user_id: str):
    """
    댓글을 삭제합니다.

    Parameters:
    - user_id (str): 삭제 권한 검증을 위한 사용자 ID (필수)
    """
    try:
        return await community_service.delete_comment(post_id, comment_id, user_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ---------------------
# --- END: 댓글 API ---
# ---------------------