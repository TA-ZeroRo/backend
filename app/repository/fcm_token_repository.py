"""FCM Token Repository"""
from typing import Optional, List, Dict, Any
from app.repository.base_repository import BaseRepository


class FcmTokenRepository(BaseRepository):
    """FCM 토큰 관련 데이터베이스 작업을 처리하는 Repository"""

    FCM_TOKEN_TABLE = "user_fcm_tokens"

    async def get_tokens_by_user_id(self, user_id: str) -> List[Dict[str, Any]]:
        """사용자 ID로 FCM 토큰 목록 조회"""
        response = (
            self.supabase
            .table(self.FCM_TOKEN_TABLE)
            .select("*")
            .eq("user_id", user_id)
            .execute()
        )
        return response.data if response.data else []

    async def get_tokens_by_user_ids(self, user_ids: List[str]) -> List[Dict[str, Any]]:
        """여러 사용자 ID로 FCM 토큰 목록 조회"""
        if not user_ids:
            return []

        response = (
            self.supabase
            .table(self.FCM_TOKEN_TABLE)
            .select("*")
            .in_("user_id", user_ids)
            .execute()
        )
        return response.data if response.data else []

    async def register_token(self, user_id: str, fcm_token: str, platform: str) -> Optional[Dict[str, Any]]:
        """FCM 토큰 등록 (이미 존재하면 업데이트)"""
        # 기존 토큰 확인
        existing = (
            self.supabase
            .table(self.FCM_TOKEN_TABLE)
            .select("*")
            .eq("user_id", user_id)
            .eq("fcm_token", fcm_token)
            .execute()
        )

        if existing.data and len(existing.data) > 0:
            # 이미 존재하면 updated_at만 갱신
            response = (
                self.supabase
                .table(self.FCM_TOKEN_TABLE)
                .update({"platform": platform})
                .eq("user_id", user_id)
                .eq("fcm_token", fcm_token)
                .execute()
            )
        else:
            # 새로 등록
            response = (
                self.supabase
                .table(self.FCM_TOKEN_TABLE)
                .insert({
                    "user_id": user_id,
                    "fcm_token": fcm_token,
                    "platform": platform
                })
                .execute()
            )

        if response.data and len(response.data) > 0:
            return response.data[0]
        return None

    async def delete_token(self, user_id: str, fcm_token: str) -> bool:
        """FCM 토큰 삭제"""
        try:
            response = (
                self.supabase
                .table(self.FCM_TOKEN_TABLE)
                .delete()
                .eq("user_id", user_id)
                .eq("fcm_token", fcm_token)
                .execute()
            )
            return response.data is not None
        except Exception:
            return False

    async def delete_all_tokens_by_user_id(self, user_id: str) -> bool:
        """사용자의 모든 FCM 토큰 삭제 (로그아웃 시)"""
        try:
            response = (
                self.supabase
                .table(self.FCM_TOKEN_TABLE)
                .delete()
                .eq("user_id", user_id)
                .execute()
            )
            return response.data is not None
        except Exception:
            return False

    async def delete_invalid_token(self, fcm_token: str) -> bool:
        """유효하지 않은 토큰 삭제 (FCM 발송 실패 시)"""
        try:
            response = (
                self.supabase
                .table(self.FCM_TOKEN_TABLE)
                .delete()
                .eq("fcm_token", fcm_token)
                .execute()
            )
            return response.data is not None
        except Exception:
            return False
