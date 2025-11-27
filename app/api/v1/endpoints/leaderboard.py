from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from uuid import UUID
from app.services.leaderboard_service import LeaderboardService
from app.schemas.leaderboard_schemas import LeaderboardUserResponse, LeaderboardResponse

router = APIRouter()
leaderboard_service = LeaderboardService()

@router.get("/ranking", response_model=LeaderboardResponse)
async def get_leaderboard_ranking(
    user_id: Optional[str] = Query(None, description="내 순위를 조회할 사용자 ID (Optional)")
):
    """
    리더보드 순위를 가져옵니다.

    Args:
        user_id: 내 순위를 조회할 사용자 ID (Optional)

    Returns:
        LeaderboardResponse: {
            "leaderboard": [...],  # 상위 50명 랭킹
            "my_rank": {...}       # 내 순위 정보 (user_id가 있을 경우)
        }
    """
    try:
        # user_id가 문자열로 제공된 경우 UUID로 변환
        user_uuid = None
        if user_id:
            try:
                user_uuid = UUID(user_id)
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid user_id format")

        result = await leaderboard_service.get_leaderboard(user_id=user_uuid)
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/ranking/{user_id}", response_model=LeaderboardUserResponse)
async def get_user_ranking(user_id: UUID):
    """
    특정 사용자의 리더보드 순위를 가져옵니다.

    Args:
        user_id: 조회할 사용자의 UUID

    Returns:
        LeaderboardUserResponse: 사용자의 전체 정보와 순위

    Raises:
        HTTPException: 사용자를 찾을 수 없거나 서버 오류 발생 시
    """
    try:
        result = await leaderboard_service.get_user_rank(user_id)

        # 사용자를 찾을 수 없는 경우
        if result is None:
            raise HTTPException(status_code=404, detail="User not found")

        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
