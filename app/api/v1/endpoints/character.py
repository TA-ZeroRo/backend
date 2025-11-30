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
    전체 캐릭터 목록과 사용자의 해금 상태를 조회합니다.
    """
    from app.config.characters import CHARACTER_PERSONALITIES, CHARACTER_MILESTONES

    user = await user_service.get_user_by_id(user_id)
    unlocked_characters = user.get("characters", [])
    total_points = user.get("total_points", 0)

    # 전체 캐릭터 정보 구성
    all_characters = []
    for char_id, char_info in CHARACTER_PERSONALITIES.items():
        required_points = CHARACTER_MILESTONES.get(char_id, 0)
        is_unlocked = char_id in unlocked_characters
        can_unlock = total_points >= required_points and not is_unlocked

        all_characters.append({
            "id": char_id,
            "name": char_info["name"],
            "description": char_info["description"],
            "greeting": char_info["greeting"],
            "is_unlocked": is_unlocked,
            "required_points": required_points,
            "can_unlock": can_unlock
        })

    return {
        "characters": all_characters,
        "total_points": total_points,
        "gacha_tickets": user.get("gacha_tickets", 0)
    }
