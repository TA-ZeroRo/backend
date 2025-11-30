"""User Service - 사용자 관련 비즈니스 로직"""
from fastapi import HTTPException
from uuid import UUID
from typing import Dict, Any
from app.repository.user_repository import UserRepository
from app.schemas.user_schemas import UserCreate, UserUpdate


class UserService:
    """사용자 관련 비즈니스 로직을 처리하는 서비스"""

    GACHA_THRESHOLD = 300  # 뽑기권 획득에 필요한 포인트

    def __init__(self):
        self.user_repo = UserRepository()

    async def get_user_by_id(self, user_id: UUID) -> Dict[str, Any]:
        """사용자 ID로 사용자 정보 조회"""
        user = await self.user_repo.get_user_by_id(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="해당 user를 찾을 수 없습니다.")
        return user

    async def create_user(self, user_data: UserCreate) -> Dict[str, Any]:
        """새로운 사용자 생성"""
        # 이미 존재하는 사용자인지 확인
        if await self.user_repo.check_user_exists(user_data.id):
            raise HTTPException(status_code=409, detail="이미 해당 uuid로 등록된 프로필이 존재합니다.")

        # 사용자 생성 (UUID, datetime을 문자열로 변환)
        user_dict = user_data.model_dump()
        user_dict["id"] = str(user_dict["id"])  # UUID → str

        # datetime 객체를 ISO 형식 문자열로 변환
        if "last_active_at" in user_dict and user_dict["last_active_at"]:
            user_dict["last_active_at"] = user_dict["last_active_at"].isoformat()

        created_user = await self.user_repo.create_user(user_dict)
        if not created_user:
            raise HTTPException(status_code=500, detail="유저 생성에 실패했습니다.")

        # 생성된 사용자 정보 조회 (추가 정보 포함)
        user = await self.user_repo.get_user_by_id(created_user["id"])
        if not user:
            raise HTTPException(status_code=500, detail="생성된 유저 조회에 실패했습니다.")
        return user

    async def update_user(self, user_id: UUID, user_data: UserUpdate) -> Dict[str, Any]:
        """사용자 정보 업데이트"""
        # 업데이트할 데이터만 추출 (None이 아닌 값만)
        update_data = {k: v for k, v in user_data.model_dump().items() if v is not None}

        if not update_data:
            raise HTTPException(status_code=400, detail="업데이트할 데이터가 없습니다.")

        # total_points가 업데이트되면 티켓 자동 지급 및 캐릭터 자동 해금
        if "total_points" in update_data:
            from app.config.characters import get_unlockable_characters

            user = await self.user_repo.get_user_by_id(user_id)
            if not user:
                raise HTTPException(status_code=404, detail="해당 user를 찾을 수 없습니다.")

            old_points = user.get("total_points", 0)
            new_points = update_data["total_points"]

            # 1. 티켓 자동 지급
            old_ticket_milestones = old_points // self.GACHA_THRESHOLD
            new_ticket_milestones = new_points // self.GACHA_THRESHOLD
            tickets_to_add = new_ticket_milestones - old_ticket_milestones

            if tickets_to_add > 0:
                current_gacha_tickets = user.get("gacha_tickets", 0)
                update_data["gacha_tickets"] = current_gacha_tickets + tickets_to_add

            # 2. 캐릭터 자동 해금
            unlockable_characters = get_unlockable_characters(new_points)
            current_characters = user.get("characters", [])

            # 새로 해금 가능한 캐릭터 찾기
            new_unlocks = [
                char for char in unlockable_characters
                if char not in current_characters
            ]

            if new_unlocks:
                update_data["characters"] = current_characters + new_unlocks

        # datetime 객체를 ISO 형식 문자열로 변환
        if "last_active_at" in update_data and update_data["last_active_at"]:
            update_data["last_active_at"] = update_data["last_active_at"].isoformat()

        updated_user = await self.user_repo.update_user(user_id, update_data)
        if not updated_user:
            raise HTTPException(status_code=500, detail="유저 수정에 실패했습니다.")

        # 업데이트된 사용자 정보 조회
        user = await self.user_repo.get_user_by_id(user_id)
        if not user:
            raise HTTPException(status_code=500, detail="수정된 유저 조회에 실패했습니다.")
        return user

    async def delete_user(self, user_id: UUID) -> Dict[str, str]:
        """사용자 삭제"""
        success = await self.user_repo.delete_user(user_id)
        if not success:
            raise HTTPException(status_code=500, detail="유저 삭제에 실패했습니다.")

        return {"message": "유저가 성공적으로 삭제되었습니다."}

    async def unlock_character(self, user_id: UUID, character_name: str) -> Dict[str, Any]:
        """캐릭터 해금"""
        from app.config.characters import CHARACTER_MILESTONES

        # 사용자 정보 조회
        user = await self.user_repo.get_user_by_id(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="해당 user를 찾을 수 없습니다.")

        # 캐릭터가 존재하는지 확인
        if character_name not in CHARACTER_MILESTONES:
            raise HTTPException(status_code=400, detail="존재하지 않는 캐릭터입니다.")

        # 이미 해금된 캐릭터인지 확인
        unlocked_characters = user.get("characters", [])
        if character_name in unlocked_characters:
            raise HTTPException(status_code=400, detail="이미 해금된 캐릭터입니다.")

        # 마일스톤 달성 여부 확인
        current_points = user.get("total_points", 0)
        required_points = CHARACTER_MILESTONES[character_name]

        if current_points < required_points:
            raise HTTPException(
                status_code=400,
                detail=f"포인트가 부족합니다. (현재: {current_points}, 필요: {required_points})"
            )

        # 캐릭터 추가
        new_characters = unlocked_characters + [character_name]

        update_data = {
            "characters": new_characters
        }

        updated_user = await self.user_repo.update_user(user_id, update_data)
        if not updated_user:
            raise HTTPException(status_code=500, detail="캐릭터 해금에 실패했습니다.")

        return {
            "message": "캐릭터가 성공적으로 해금되었습니다.",
            "character_name": character_name,
            "current_points": current_points,
            "unlocked_characters": new_characters
        }

    async def gacha_personality(self, user_id: UUID) -> Dict[str, Any]:
        """성격 뽑기 (티켓 1개 소모)"""
        from app.config.personalities import get_random_personality

        # 사용자 정보 조회
        user = await self.user_repo.get_user_by_id(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="해당 user를 찾을 수 없습니다.")

        # 현재 티켓 확인
        current_tickets = user.get("gacha_tickets", 0)

        # 뽑기 가능 여부 확인 (티켓 1개 이상 필요)
        if current_tickets < 1:
            raise HTTPException(
                status_code=400,
                detail=f"사용 가능한 뽑기권이 없습니다. (현재 티켓: {current_tickets})"
            )

        # 랜덤 성격 뽑기
        personality = get_random_personality()

        # 티켓 1개 차감
        new_tickets = current_tickets - 1
        update_data = {"gacha_tickets": new_tickets}

        updated_user = await self.user_repo.update_user(user_id, update_data)
        if not updated_user:
            raise HTTPException(status_code=500, detail="티켓 차감에 실패했습니다.")

        return {
            "personality": {
                "id": personality["id"],
                "name": personality["name"],
                "description": personality["description"]
            },
            "remaining_tickets": new_tickets
        }
