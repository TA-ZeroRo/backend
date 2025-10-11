from fastapi import APIRouter, HTTPException
from app.services.leaderboard_service import LeaderboardService

router = APIRouter()
leaderboard_service = LeaderboardService()

@router.get("/ranking")
async def get_leaderboard_ranking():
    """
    리더보드 순위를 가져옵니다.
    """
    try:
        return await leaderboard_service.get_leaderboard()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
