from fastapi import APIRouter
from pydantic import BaseModel
from uuid import UUID
from typing import List
from app.services.user_service import UserService

router = APIRouter()
user_service = UserService()


class CharacterUnlockRequest(BaseModel):
    """캐릭터 해금 요청"""
    user_id: UUID
    character_name: str


@router.post("/unlock")
async def unlock_character(request: CharacterUnlockRequest):
    """
    캐릭터를 해금합니다. (300포인트 필요)
    """
    result = await user_service.unlock_character(
        user_id=request.user_id,
        character_name=request.character_name
    )
    return result


@router.get("/{user_id}")
async def get_user_characters(user_id: UUID):
    """
    사용자의 해금된 캐릭터 목록을 조회합니다.
    """
    user = await user_service.get_user_by_id(user_id)
    return {
        "characters": user.get("characters", []),
        "total_points": user.get("total_points", 0)
    }
