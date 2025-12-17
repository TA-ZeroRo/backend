from fastapi import APIRouter, HTTPException
from uuid import UUID
from app.services.user_service import UserService
from app.config.personalities import get_random_personality, PERSONALITY_TYPES
from app.schemas.user_schemas import UserUpdate

router = APIRouter()
user_service = UserService()


@router.get("/{user_id}")
async def get_user_personalities(user_id: UUID):
    """
    사용자가 보유한 성격 목록과 전체 성격 정보를 조회합니다.

    Returns:
        - personalities: 전체 성격 목록 (보유 여부 포함)
        - owned_personalities: 보유한 성격 ID 목록
    """
    user = await user_service.get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="해당 사용자를 찾을 수 없습니다.")

    owned_personalities = user.get("personalities", [])

    # 전체 성격 정보 구성
    all_personalities = []
    for personality_id, personality_info in PERSONALITY_TYPES.items():
        is_owned = personality_id in owned_personalities

        all_personalities.append({
            "id": personality_id,
            "name": personality_info["name"],
            "description": personality_info["description"],
            "is_owned": is_owned
        })

    return {
        "personalities": all_personalities,
        "owned_personalities": owned_personalities,
        "gacha_tickets": user.get("gacha_tickets", 0)
    }


@router.post("/gacha")
async def gacha_personality(user_id: UUID):
    """
    성격 뽑기를 수행합니다.

    Returns:
        - personality: 뽑은 성격 정보
        - is_new: 새로 획득한 성격인지 여부
    """
    user = await user_service.get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="해당 사용자를 찾을 수 없습니다.")

    # 가챠 티켓 확인
    gacha_tickets = user.get("gacha_tickets", 0)
    if gacha_tickets <= 0:
        raise HTTPException(
            status_code=400,
            detail="사용 가능한 뽑기권이 없습니다. 포인트를 모아서 뽑기권을 획득하세요."
        )

    # 랜덤 성격 뽑기
    drawn_personality = get_random_personality()
    personality_id = drawn_personality["id"]

    # 이미 보유한 성격인지 확인
    owned_personalities = user.get("personalities", [])
    is_new = personality_id not in owned_personalities

    # 새로운 성격이면 personalities 배열에 추가
    if is_new:
        owned_personalities.append(personality_id)

    # DB 업데이트 (티켓 차감 + 성격 추가)
    update_data = UserUpdate(
        gacha_tickets=gacha_tickets - 1,
        personalities=owned_personalities if is_new else None
    )
    await user_service.update_user(user_id=user_id, user_data=update_data)

    return {
        "personality": {
            "id": personality_id,
            "name": drawn_personality["name"],
            "description": drawn_personality["description"]
        },
        "is_new": is_new,
        "remaining_tickets": gacha_tickets - 1
    }
