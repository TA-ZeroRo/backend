from fastapi import APIRouter

router = APIRouter()

@router.get("/")
async def get_verification():
    return {"message": "Verification endpoint"}
