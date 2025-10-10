from fastapi import APIRouter, HTTPException
from typing import Optional
from app.services.community_service import CommunityService
from app.schemas.community_schemas import PostCreate, PostUpdate

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

    Returns:
    - posts (List[PostResponse]): 게시글 목록 (프로필 정보 포함)
    """
    try:
        return await community_service.get_posts(offset=offset, user_id=user_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/posts")
async def create_community_post(post_data: PostCreate):
    """
    새로운 커뮤니티 게시글을 생성합니다.

    Parameters:
    - post_data (PostCreate): 게시글 생성 데이터
      - title (str): 게시글 제목
      - content (str): 게시글 내용
      - user_id (UUID): 작성자 ID
      - image_url (str, optional): 이미지 URL

    Returns:
    - post (PostResponse): 생성된 게시글 정보 (프로필 정보 포함)
    """
    try:
        return await community_service.create_post(post_data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/posts/{post_id}")
async def update_community_post(post_id: int, post_data: PostUpdate):
    """
    커뮤니티 게시글을 수정합니다.

    Parameters:
    - post_id (int): 수정할 게시글 ID
    - post_data (PostUpdate): 수정할 데이터
      - title (str, optional): 수정할 제목
      - content (str, optional): 수정할 내용
      - image_url (str, optional): 수정할 이미지 URL

    Returns:
    - post (PostResponse): 수정된 게시글 정보 (프로필 정보 포함)
    """
    try:
        return await community_service.update_post(post_id, post_data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/posts/{post_id}")
async def delete_community_post(post_id: int):
    """
    커뮤니티 게시글을 삭제합니다.

    Parameters:
    - post_id (int): 삭제할 게시글 ID

    Returns:
    - message (str): 삭제 성공 메시지
    """
    try:
        return await community_service.delete_post(post_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
# -----------------------
# --- END: 게시글 API ---
# -----------------------
