from fastapi import APIRouter

router = APIRouter()

@router.get("/")
async def get_points():
    return {"message": "Point endpoint"}
