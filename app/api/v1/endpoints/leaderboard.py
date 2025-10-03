from fastapi import APIRouter

router = APIRouter()

@router.get("/")
async def get_leaderboard():
    return {"message": "Leaderboard endpoint"}
