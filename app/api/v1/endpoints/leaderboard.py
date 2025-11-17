from fastapi import APIRouter, HTTPException
from typing import List
from uuid import UUID
from app.services.leaderboard_service import LeaderboardService
from app.schemas.leaderboard_schemas import LeaderboardUserResponse

router = APIRouter()
leaderboard_service = LeaderboardService()

@router.get("/ranking", response_model=List[LeaderboardUserResponse])
async def get_leaderboard_ranking():
    """
    리더보드 순위를 가져옵니다.
    """
    try:
        result = await leaderboard_service.get_leaderboard()
        return result["leaderboard"]
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
