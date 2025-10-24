"""User Repository"""
from typing import Optional, Dict, Any
from uuid import UUID
from datetime import datetime
from app.repository.base_repository import BaseRepository


class UserRepository(BaseRepository):
    """사용자 관련 데이터베이스 작업을 처리하는 Repository"""

    TABLE_NAME = "profiles"

    async def get_user_by_id(self, user_id: UUID) -> Optional[Dict[str, Any]]:
        """사용자 ID로 사용자 정보 조회"""
        return await self.find_by_id(self.TABLE_NAME, str(user_id))

    async def create_user(self, user_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """새로운 사용자 생성"""
        # 필수 필드 보장
        user_data.setdefault("total_points", 0)
        user_data.setdefault("continuous_days", 0)
        user_data.setdefault("last_active_at", datetime.now().isoformat())
        user_data.setdefault("created_at", datetime.now().isoformat())
        return await self.create(self.TABLE_NAME, user_data)

    async def update_user(self, user_id: UUID, user_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """사용자 정보 업데이트"""
        # 마지막 활동 시간 자동 업데이트
        update_data = user_data.copy()
        update_data["last_active_at"] = datetime.now().isoformat()
        return await self.update(self.TABLE_NAME, str(user_id), update_data)
        

    async def delete_user(self, user_id: UUID) -> bool:
        """사용자 삭제"""
        return await self.delete(self.TABLE_NAME, str(user_id))

    async def check_user_exists(self, user_id: UUID) -> bool:
        """사용자 존재 여부 확인"""
        response = (
            self.supabase
            .table(self.TABLE_NAME)
            .select("id")
            .eq("id", str(user_id))
            .execute()
        )
        return bool(response.data)
