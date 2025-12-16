"""Mission Log Service - 미션 로그 관련 비즈니스 로직"""
import logging
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from uuid import UUID
from app.repository.mission_log_repository import MissionLogRepository
from app.repository.mission_template_repository import MissionTemplateRepository
from app.repository.point_log_repository import PointLogRepository
from app.repository.user_repository import UserRepository
from app.services.verification_service import VerificationService

logger = logging.getLogger(__name__)


class MissionLogService:
    """미션 로그 관련 비즈니스 로직을 처리하는 서비스"""

    def __init__(self):
        self.mission_log_repo = MissionLogRepository()
        self.point_log_repo = PointLogRepository()
        self.user_repo = UserRepository()
        self.template_repo = MissionTemplateRepository()
        self.verification_service = VerificationService()

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
        증빙 데이터 제출 및 상태 변경 (+ AI 자동 검증)

        - 위치 인증: 바로 COMPLETED 처리 (검수 불필요)
        - 기타 인증: PENDING_VERIFICATION 상태로 변경 (Console에서 최종 승인)
        - IMAGE/TEXT_REVIEW: success_criteria 기반 AI 자동 검증 수행

        Parameters:
        - log_id: 미션 로그 ID
        - proof_data: 증빙 데이터
          - verification_type: 인증 유형 ('location' = 위치 인증)
          - verification_result: AI 검증 결과 (is_valid, confidence, reason)
          - imageUrl, text 등: 실제 증빙 데이터
          - 오류 판단 기준: error, error_message, failed 필드가 있으면 FAILED

        Returns:
        - 업데이트된 미션 로그 정보
        """
        current_log = await self._get_log_or_raise(log_id)
        current_status = current_log.get("status")
        has_error = (
            "error" in proof_data or
            "error_message" in proof_data or
            proof_data.get("failed") is True
        )

        # IN_PROGRESS 상태가 아니면 증빙 데이터만 업데이트
        if current_status != "IN_PROGRESS":
            await self._update_log_or_raise(log_id, {"proof_data": proof_data})
            return await self.mission_log_repo.get_log_by_id(log_id)

        # 위치 인증은 바로 COMPLETED 처리 (검수 불필요)
        is_location_verification = proof_data.get("verification_type") == "location"

        if has_error:
            new_status = "FAILED"
        elif is_location_verification:
            # 위치 인증: 바로 완료 처리
            new_status = "COMPLETED"
        else:
            # 기타 인증: 검수 대기
            new_status = "PENDING_VERIFICATION"

        # AI 자동 검증 수행 (IMAGE, TEXT_REVIEW 타입만)
        if new_status == "PENDING_VERIFICATION" and not has_error:
            proof_data = await self._perform_ai_verification(current_log, proof_data)

        update_data = {
            "status": new_status,
            "proof_data": proof_data,
        }

        # COMPLETED 상태면 완료 시간 추가
        if new_status == "COMPLETED":
            update_data["completed_at"] = datetime.now(timezone.utc).isoformat()

        await self._update_log_or_raise(log_id, update_data)

        # COMPLETED 상태면 포인트 지급
        if new_status == "COMPLETED":
            await self._award_points_for_completion(current_log)

        return await self.mission_log_repo.get_log_by_id(log_id)

    async def _perform_ai_verification(
        self,
        current_log: Dict[str, Any],
        proof_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        success_criteria 기반 AI 자동 검증 수행

        Parameters:
        - current_log: 현재 미션 로그
        - proof_data: 증빙 데이터

        Returns:
        - verification_result가 추가된 proof_data
        """
        try:
            # 미션 템플릿 정보 가져오기
            template_id = current_log.get("mission_template_id")
            if not template_id:
                return proof_data

            template = await self.template_repo.get_template_by_id(template_id)
            if not template:
                return proof_data

            verification_type = template.get("verification_type", "")
            success_criteria = template.get("success_criteria", "")
            mission_title = template.get("title", "")

            # AI 검증이 필요한 타입인지 확인
            if verification_type not in ["IMAGE", "TEXT_REVIEW"]:
                return proof_data

            # success_criteria가 없으면 스킵
            if not success_criteria:
                return proof_data

            # AI 검증 수행
            logger.info(f"AI 검증 시작: log_id={current_log.get('id')}, type={verification_type}")
            verification_result = await self.verification_service.verify_with_criteria(
                verification_type=verification_type,
                proof_data=proof_data,
                success_criteria=success_criteria,
                mission_title=mission_title
            )

            # 검증 결과를 proof_data에 추가
            proof_data["verification_result"] = verification_result
            logger.info(f"AI 검증 완료: is_valid={verification_result.get('is_valid')}, confidence={verification_result.get('confidence')}")

        except Exception as e:
            logger.error(f"AI 검증 중 오류 발생: {str(e)}", exc_info=True)
            # 오류가 발생해도 기존 proof_data 반환 (검증 실패로 처리하지 않음)

        return proof_data

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
        current_log = await self._get_log_or_raise(log_id)
        update_data: Dict[str, Any] = {"status": status}

        # completed_at 처리
        if completed_at is not None:
            update_data["completed_at"] = completed_at
        elif status == "COMPLETED" and not current_log.get("completed_at"):
            update_data["completed_at"] = datetime.now(timezone.utc).isoformat()
        elif status != "COMPLETED":
            update_data["completed_at"] = None

        if proof_data is not None:
            update_data["proof_data"] = proof_data

        await self._update_log_or_raise(log_id, update_data)

        # COMPLETED 상태로 변경된 경우 포인트 지급
        if status == "COMPLETED" and current_log.get("status") != "COMPLETED":
            await self._award_points_for_completion(current_log)

        return await self.mission_log_repo.get_log_by_id(log_id)

    async def _get_log_or_raise(self, log_id: int) -> Dict[str, Any]:
        """미션 로그 조회 또는 예외 발생"""
        log = await self.mission_log_repo.get_log_by_id(log_id)
        if not log:
            raise ValueError(f"미션 로그 ID {log_id}를 찾을 수 없습니다.")
        return log

    async def _update_log_or_raise(self, log_id: int, update_data: Dict[str, Any]) -> None:
        """미션 로그 업데이트 또는 예외 발생"""
        updated = await self.mission_log_repo.update_log(log_id, update_data)
        if not updated:
            raise ValueError(
                f"미션 로그 업데이트에 실패했습니다. "
                f"미션 로그 ID {log_id}가 존재하지 않거나 업데이트할 수 없습니다."
            )

    async def _award_points_for_completion(self, mission_log: Dict[str, Any]) -> None:
        """미션 완료 시 포인트 지급"""
        try:
            user_id_str = mission_log.get("user_id")
            if not user_id_str:
                logger.warning("포인트 지급 실패: user_id가 없습니다")
                return

            user_id = UUID(user_id_str)

            # 미션 템플릿에서 보상 포인트 가져오기
            mission_template = mission_log.get("mission_templates")
            if not mission_template:
                template_id = mission_log.get("mission_template_id")
                if not template_id:
                    logger.error("포인트 지급 실패: mission_template_id가 없습니다")
                    return
                mission_template = await self.template_repo.get_template_by_id(template_id)
                if not mission_template:
                    logger.error("포인트 지급 실패: mission_template 조회 실패")
                    return

            reward_points = mission_template.get("reward_points", 0)
            if reward_points <= 0:
                return

            # 사용자 정보 조회
            user_data = await self.user_repo.get_user_by_id(user_id)
            if not user_data:
                return

            # 포인트 로그 생성 및 사용자 포인트 업데이트
            point_log = await self.point_log_repo.create_point_log(
                user_id=user_id,
                point=reward_points
            )
            if not point_log:
                raise ValueError("포인트 로그 생성에 실패했습니다.")

            new_total_points = user_data.get("total_points", 0) + reward_points
            updated_user = await self.user_repo.update_user(
                user_id=user_id,
                user_data={"total_points": new_total_points}
            )
            if not updated_user:
                raise ValueError("사용자 포인트 업데이트에 실패했습니다.")

            logger.info(f"포인트 지급 완료: user_id={user_id}, points={reward_points}, total={new_total_points}")

        except Exception as e:
            logger.error(f"미션 완료 포인트 지급 실패: {str(e)}", exc_info=True)
