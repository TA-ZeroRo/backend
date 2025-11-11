from fastapi import APIRouter, HTTPException
from typing import List
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
