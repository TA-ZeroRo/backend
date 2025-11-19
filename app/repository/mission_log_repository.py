"""MissionLog Repository"""
from typing import List, Dict, Any, Optional
from uuid import UUID
from app.repository.base_repository import BaseRepository
from postgrest.exceptions import APIError


class MissionLogRepository(BaseRepository):
    """미션 로그 관련 데이터베이스 작업을 처리하는 Repository"""

    TABLE_NAME = "mission_logs"

    async def get_by_user_id(self, user_id: UUID) -> List[Dict[str, Any]]:
        """
        사용자 ID로 미션 로그 목록 조회 (템플릿 및 캠페인 정보 포함)

        Parameters:
        - user_id: 사용자 UUID

        Returns:
        - 미션 로그 목록 (최신순, 템플릿 및 캠페인 정보 포함)
        """
        select_query = "*, mission_templates(*, campaigns(*))"

        response = (
            self.supabase
            .table(self.TABLE_NAME)
            .select(select_query)
            .eq("user_id", str(user_id))
            .order("started_at", desc=True)
            .execute()
        )
        return response.data if response.data else []

    async def get_by_user_and_template(
        self,
        user_id: UUID,
        mission_template_id: int
    ) -> Optional[Dict[str, Any]]:
        """
        특정 사용자의 특정 미션 템플릿 로그 조회

        Parameters:
        - user_id: 사용자 UUID
        - mission_template_id: 미션 템플릿 ID

        Returns:
        - 미션 로그 정보 또는 None
        """
        try:
            response = (
                self.supabase
                .table(self.TABLE_NAME)
                .select("*")
                .eq("user_id", str(user_id))
                .eq("mission_template_id", mission_template_id)
                .single()
                .execute()
            )
            return response.data if response.data else None
        except APIError as e:
            # PGRST116: 결과가 0개일 때 발생하는 에러
            if e.code == "PGRST116":
                return None
            raise

    async def get_by_template_id(self, mission_template_id: int) -> List[Dict[str, Any]]:
        """
        미션 템플릿 ID로 미션 로그 목록 조회 (사용자 정보 포함)

        Parameters:
        - mission_template_id: 미션 템플릿 ID

        Returns:
        - 미션 로그 목록 (사용자 정보 포함)
        """
        select_query = "*, profiles(*)"

        response = (
            self.supabase
            .table(self.TABLE_NAME)
            .select(select_query)
            .eq("mission_template_id", mission_template_id)
            .order("started_at", desc=True)
            .execute()
        )
        return response.data if response.data else []

    async def get_log_by_id(self, log_id: int) -> Optional[Dict[str, Any]]:
        """
        미션 로그 ID로 단일 로그 조회 (템플릿, 캠페인, 사용자 정보 포함)

        Parameters:
        - log_id: 미션 로그 ID

        Returns:
        - 미션 로그 정보 또는 None
        """
        select_query = "*, mission_templates(*, campaigns(*)), profiles(*)"

        try:
            response = (
                self.supabase
                .table(self.TABLE_NAME)
                .select(select_query)
                .eq("id", log_id)
                .single()
                .execute()
            )
            return response.data if response.data else None
        except APIError as e:
            if e.code == "PGRST116":
                return None
            raise

    async def create_log(self, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        미션 로그 생성

        Parameters:
        - data: 미션 로그 데이터

        Returns:
        - 생성된 로그 정보
        """
        return await self.create(self.TABLE_NAME, data)

    async def update_log(self, log_id: int, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        미션 로그 업데이트

        Parameters:
        - log_id: 미션 로그 ID
        - data: 업데이트할 데이터

        Returns:
        - 업데이트된 로그 정보
        """
        return await self.update(self.TABLE_NAME, str(log_id), data)

    async def delete_log(self, log_id: int) -> bool:
        """
        미션 로그 삭제

        Parameters:
        - log_id: 미션 로그 ID

        Returns:
        - 삭제 성공 여부
        """
        return await self.delete(self.TABLE_NAME, str(log_id))

    async def get_by_user_and_status(
        self,
        user_id: UUID,
        status: str
    ) -> List[Dict[str, Any]]:
        """
        사용자 ID와 상태로 미션 로그 목록 조회 (템플릿 및 캠페인 정보 포함)

        Parameters:
        - user_id: 사용자 UUID
        - status: 미션 상태 (IN_PROGRESS, PENDING_VERIFICATION, COMPLETED, FAILED)

        Returns:
        - 미션 로그 목록 (템플릿 및 캠페인 정보 포함)
        """
        select_query = "*, mission_templates(*, campaigns(*))"

        response = (
            self.supabase
            .table(self.TABLE_NAME)
            .select(select_query)
            .eq("user_id", str(user_id))
            .eq("status", status)
            .order("started_at", desc=True)
            .execute()
        )
        return response.data if response.data else []

    async def get_by_campaign_id(
        self,
        campaign_id: int,
        user_id: Optional[UUID] = None
    ) -> List[Dict[str, Any]]:
        """
        캠페인 ID로 미션 로그 목록 조회 (템플릿 및 사용자 정보 포함)

        Parameters:
        - campaign_id: 캠페인 ID
        - user_id: 특정 사용자로 필터링 (선택사항)

        Returns:
        - 미션 로그 목록 (템플릿 및 사용자 정보 포함)
        """
        select_query = "*, mission_templates!inner(*), profiles(*)"

        query = (
            self.supabase
            .table(self.TABLE_NAME)
            .select(select_query)
            .eq("mission_templates.campaign_id", campaign_id)
        )

        if user_id:
            query = query.eq("user_id", str(user_id))

        response = query.order("started_at", desc=True).execute()
        return response.data if response.data else []
