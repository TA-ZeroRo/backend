"""Mission Log Service - 미션 로그 관련 비즈니스 로직"""
from typing import Dict, Any, List, Optional
from uuid import UUID
from app.repository.mission_log_repository import MissionLogRepository


class MissionLogService:
    """미션 로그 관련 비즈니스 로직을 처리하는 서비스"""

    def __init__(self):
        self.mission_log_repo = MissionLogRepository()

    async def get_mission_logs_by_user(self, user_id: UUID) -> List[Dict[str, Any]]:
        """
        사용자의 미션 로그 목록 조회 (템플릿 및 캠페인 정보 포함)

        Parameters:
        - user_id: 사용자 UUID

        Returns:
        - 미션 로그 목록 (템플릿 및 캠페인 정보 포함)
        """
        return await self.mission_log_repo.get_by_user_id(user_id)

    async def get_mission_log_by_id(self, log_id: int) -> Optional[Dict[str, Any]]:
        """
        미션 로그 ID로 단일 로그 조회 (템플릿, 캠페인, 사용자 정보 포함)

        Parameters:
        - log_id: 미션 로그 ID

        Returns:
        - 미션 로그 정보 또는 None
        """
        return await self.mission_log_repo.get_log_by_id(log_id)

    async def get_mission_logs_by_template(
        self,
        mission_template_id: int
    ) -> List[Dict[str, Any]]:
        """
        미션 템플릿 ID로 미션 로그 목록 조회 (사용자 정보 포함)

        Parameters:
        - mission_template_id: 미션 템플릿 ID

        Returns:
        - 미션 로그 목록 (사용자 정보 포함)
        """
        return await self.mission_log_repo.get_by_template_id(mission_template_id)

    async def get_mission_logs_by_user_and_status(
        self,
        user_id: UUID,
        status: str
    ) -> List[Dict[str, Any]]:
        """
        사용자 ID와 상태로 미션 로그 목록 조회 (템플릿 및 캠페인 정보 포함)

        Parameters:
        - user_id: 사용자 UUID
        - status: 미션 상태

        Returns:
        - 미션 로그 목록 (템플릿 및 캠페인 정보 포함)
        """
        return await self.mission_log_repo.get_by_user_and_status(user_id, status)

    async def get_mission_logs_by_campaign(
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
        return await self.mission_log_repo.get_by_campaign_id(
            campaign_id,
            user_id=user_id
        )

    async def get_user_mission_by_template(
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
        return await self.mission_log_repo.get_by_user_and_template(
            user_id,
            mission_template_id
        )

    async def submit_proof_data(
        self,
        log_id: int,
        proof_data: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        증빙 데이터 제출 및 상태 자동 변경

        증빙 데이터가 들어올 때 자동으로 상태를 판단합니다:
        - 정상 데이터: IN_PROGRESS -> COMPLETED
        - 오류 데이터: IN_PROGRESS -> FAILED

        Parameters:
        - log_id: 미션 로그 ID
        - proof_data: 증빙 데이터
          - 오류 판단 기준: error, error_message, failed 필드가 있으면 FAILED
          - 그 외에는 COMPLETED로 처리

        Returns:
        - 업데이트된 미션 로그 정보
        """
        # 현재 미션 로그 상태 확인
        current_log = await self.mission_log_repo.get_log_by_id(log_id)
        if not current_log:
            raise ValueError(f"미션 로그 ID {log_id}를 찾을 수 없습니다.")

        current_status = current_log.get("status")

        # 증빙 데이터에서 오류 여부 판단
        has_error = (
            "error" in proof_data or
            "error_message" in proof_data or
            proof_data.get("failed") is True
        )

        # IN_PROGRESS 상태가 아니면 상태 변경하지 않음 (증빙 데이터만 업데이트)
        if current_status != "IN_PROGRESS":
            update_data: Dict[str, Any] = {"proof_data": proof_data}
            updated = await self.mission_log_repo.update_log(log_id, update_data)
            if not updated:
                raise ValueError(
                    f"미션 로그 업데이트에 실패했습니다. "
                    f"미션 로그 ID {log_id}가 존재하지 않거나 업데이트할 수 없습니다."
                )
            return await self.mission_log_repo.get_log_by_id(log_id)

        # 상태 결정: 오류가 있으면 FAILED, 없으면 COMPLETED
        from datetime import datetime, timezone
        if has_error:
            # 실패 플로우: IN_PROGRESS -> FAILED
            # Supabase에서 null로 설정하기 위해 명시적으로 None 포함
            update_data: Dict[str, Any] = {
                "status": "FAILED",
                "proof_data": proof_data,
                "completed_at": None  # 명시적으로 None 설정하여 null로 업데이트
            }
        else:
            # 직접 완료 플로우: IN_PROGRESS -> COMPLETED
            update_data: Dict[str, Any] = {
                "status": "COMPLETED",
                "proof_data": proof_data,
                "completed_at": datetime.now(timezone.utc).isoformat()
            }

        # 업데이트 실행
        updated = await self.mission_log_repo.update_log(log_id, update_data)
        if not updated:
            raise ValueError(
                f"미션 로그 업데이트에 실패했습니다. "
                f"미션 로그 ID {log_id}가 존재하지 않거나 업데이트할 수 없습니다."
            )

        # 업데이트 후 JOIN된 데이터를 포함하여 다시 조회
        return await self.mission_log_repo.get_log_by_id(log_id)

    async def update_mission_log_status(
        self,
        log_id: int,
        status: str,
        proof_data: Optional[Dict[str, Any]] = None,
        completed_at: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """
        미션 로그 상태 수동 업데이트 (모든 상태 변경 가능)

        Parameters:
        - log_id: 미션 로그 ID
        - status: 변경할 상태 (모든 상태 허용)
        - proof_data: 증빙 데이터 (선택사항)
        - completed_at: 완료 시간 (선택사항, COMPLETED 상태일 때만 의미 있음)

        Returns:
        - 업데이트된 미션 로그 정보
        """
        # 현재 미션 로그 상태 확인
        current_log = await self.mission_log_repo.get_log_by_id(log_id)
        if not current_log:
            raise ValueError(f"미션 로그 ID {log_id}를 찾을 수 없습니다.")

        # 업데이트할 데이터 준비
        update_data: Dict[str, Any] = {
            "status": status
        }

        # completed_at 처리
        if completed_at is not None:
            update_data["completed_at"] = completed_at
        elif status == "COMPLETED" and not current_log.get("completed_at"):
            # COMPLETED 상태인데 completed_at이 없으면 현재 시간 설정
            from datetime import datetime, timezone
            update_data["completed_at"] = datetime.now(timezone.utc).isoformat()
        elif status != "COMPLETED":
            # COMPLETED가 아닌 상태로 변경 시 completed_at 제거
            update_data["completed_at"] = None

        # 증빙 데이터가 있으면 추가
        if proof_data is not None:
            update_data["proof_data"] = proof_data

        # 업데이트 실행
        updated = await self.mission_log_repo.update_log(log_id, update_data)
        if not updated:
            raise ValueError(
                f"미션 로그 업데이트에 실패했습니다. "
                f"미션 로그 ID {log_id}가 존재하지 않거나 업데이트할 수 없습니다."
            )

        # 업데이트 후 JOIN된 데이터를 포함하여 다시 조회
        return await self.mission_log_repo.get_log_by_id(log_id)