"""Mission Log Service - 미션 로그 관련 비즈니스 로직"""
from typing import Dict, Any, List, Optional
from uuid import UUID
from app.repository.mission_log_repository import MissionLogRepository
from app.repository.point_log_repository import PointLogRepository
from app.repository.user_repository import UserRepository


class MissionLogService:
    """미션 로그 관련 비즈니스 로직을 처리하는 서비스"""

    def __init__(self):
        self.mission_log_repo = MissionLogRepository()
        self.point_log_repo = PointLogRepository()
        self.user_repo = UserRepository()

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

        # COMPLETED 상태로 변경된 경우 포인트 지급 (중복 지급 방지)
        if not has_error and current_status != "COMPLETED":
            await self._award_points_for_completion(current_log)

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

        # COMPLETED 상태로 변경된 경우 포인트 지급 (중복 지급 방지)
        if status == "COMPLETED" and current_log.get("status") != "COMPLETED":
            await self._award_points_for_completion(current_log)

        # 업데이트 후 JOIN된 데이터를 포함하여 다시 조회
        return await self.mission_log_repo.get_log_by_id(log_id)

    async def _award_points_for_completion(self, mission_log: Dict[str, Any]) -> None:
        """
        미션 완료 시 포인트 지급

        Parameters:
        - mission_log: 미션 로그 정보 (mission_templates 정보 포함)
        """
        try:
            # 사용자 ID 추출
            user_id_str = mission_log.get("user_id")
            if not user_id_str:
                return

            user_id = UUID(user_id_str)

            # 미션 템플릿에서 보상 포인트 가져오기
            mission_template = mission_log.get("mission_templates")
            if not mission_template:
                # mission_templates가 JOIN되지 않은 경우 직접 조회
                template_id = mission_log.get("mission_template_id")
                if not template_id:
                    return
                
                from app.repository.mission_template_repository import MissionTemplateRepository
                template_repo = MissionTemplateRepository()
                mission_template = await template_repo.get_template_by_id(template_id)
                if not mission_template:
                    return

            reward_points = mission_template.get("reward_points", 0)
            if reward_points <= 0:
                # 보상 포인트가 없으면 지급하지 않음
                return

            # 현재 사용자 정보 조회 (total_points 확인)
            user_data = await self.user_repo.get_user_by_id(user_id)
            if not user_data:
                return

            current_total_points = user_data.get("total_points", 0)

            # 1. 포인트 로그 생성
            point_log = await self.point_log_repo.create_point_log(
                user_id=user_id,
                point=reward_points
            )
            if not point_log:
                raise ValueError("포인트 로그 생성에 실패했습니다.")

            # 2. 사용자 total_points 업데이트
            new_total_points = current_total_points + reward_points
            updated_user = await self.user_repo.update_user(
                user_id=user_id,
                user_data={"total_points": new_total_points}
            )
            if not updated_user:
                raise ValueError("사용자 포인트 업데이트에 실패했습니다.")

        except Exception as e:
            # 포인트 지급 실패는 로그만 남기고 예외를 던지지 않음
            # (미션 완료 자체는 성공했으므로)
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"미션 완료 포인트 지급 실패: {str(e)}")