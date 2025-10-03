from fastapi import APIRouter

router = APIRouter()

@router.get("/")
async def get_characters():
    return {"message": "Character endpoint"}
