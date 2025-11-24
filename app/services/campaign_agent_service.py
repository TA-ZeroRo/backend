"""Campaign Agent Service - 자동화된 캠페인 에이전트 비즈니스 로직"""
import logging
from typing import Dict, Any, Optional, List
from uuid import UUID
from datetime import datetime

from app.repository.campaign_repository import CampaignRepository
from app.repository.mission_template_repository import MissionTemplateRepository
from app.repository.mission_log_repository import MissionLogRepository
from app.repository.user_repository import UserRepository
from app.repository.point_log_repository import PointLogRepository
# Deprecated: 2025-01-22 - Moved to WebView RPA
# from app.repository.rpa_config_repository import RPAConfigRepository
# from app.services.rpa_core import submit_eco_mileage_form, submit_with_hybrid_config

logger = logging.getLogger(__name__)


class CampaignAgentService:
    """
    자동화된 캠페인 에이전트 서비스

    캠페인 참여, 미션 수행, RPA 자동 제출 등을 처리하는 비즈니스 로직 계층
    """

    def __init__(self):
        self.campaign_repo = CampaignRepository()
        self.mission_template_repo = MissionTemplateRepository()
        self.mission_log_repo = MissionLogRepository()
        self.user_repo = UserRepository()
        self.point_log_repo = PointLogRepository()
        # Deprecated: 2025-01-22 - Moved to WebView RPA
        # self.rpa_config_repo = RPAConfigRepository()

    async def start_campaign(
        self,
        user_id: UUID,
        campaign_id: int
    ) -> Dict[str, Any]:
        """
        사용자의 캠페인 시작 및 미션 로그 생성

        Parameters:
        -----------
        user_id : UUID
            사용자 ID
        campaign_id : int
            캠페인 ID

        Returns:
        --------
        Dict[str, Any]
            {
                "campaign_id": 1,
                "missions_created": 3,
                "mission_logs": [...]
            }
        """
        try:
            # 캠페인 존재 확인
            campaign = await self.campaign_repo.get_campaign_by_id(campaign_id)
            if not campaign:
                logger.error(f"Campaign {campaign_id} not found")
                return {
                    "success": False,
                    "error": "Campaign not found"
                }

            # 캠페인의 미션 템플릿 조회
            templates = await self.mission_template_repo.get_by_campaign_id(campaign_id)
            if not templates:
                logger.warning(f"캠페인 미션이 존재하지 않습니다. {campaign_id}")
                return {
                    "success": False,
                    "error": "캠페인 미션이 존재하지 않습니다."
                }

            # 각 미션 템플릿에 대한 로그 생성
            mission_logs = []
            for template in templates:
                # 이미 존재하는 로그 확인
                existing_log = await self.mission_log_repo.get_by_user_and_template(
                    user_id,
                    template['id']
                )

                if existing_log:
                    logger.info(f"Mission log already exists for user {user_id}, template {template['id']}")
                    mission_logs.append(existing_log)
                    continue

                # 새 미션 로그 생성
                log_data = {
                    "user_id": str(user_id),
                    "mission_template_id": template['id'],
                    "status": "IN_PROGRESS",
                    "started_at": datetime.utcnow().isoformat()
                }

                created_log = await self.mission_log_repo.create_log(log_data)
                if created_log:
                    mission_logs.append(created_log)
                    logger.info(f"Created mission log for user {user_id}, template {template['id']}")

            return {
                "success": True,
                "campaign_id": campaign_id,
                "missions_created": len(mission_logs),
                "mission_logs": mission_logs
            }

        except Exception as e:
            logger.error(f"Error starting campaign: {str(e)}", exc_info=True)
            return {
                "success": False,
                "error": f"Failed to start campaign: {str(e)}"
            }

    async def submit_mission_with_rpa(
        self,
        user_id: UUID,
        mission_log_id: int,
        submission_data: Dict[str, Any],
        credentials: Dict[str, str]
    ) -> Dict[str, Any]:
        """
        RPA를 사용하여 미션 자동 제출

        Parameters:
        -----------
        user_id : UUID
            사용자 ID
        mission_log_id : int
            미션 로그 ID
        submission_data : Dict[str, Any]
            제출할 폼 데이터
        credentials : Dict[str, str]
            로그인 인증 정보

        Returns:
        --------
        Dict[str, Any]
            RPA 실행 결과 및 업데이트된 미션 로그
        """
        try:
            # 미션 로그 조회 및 권한 확인
            mission_log = await self.mission_log_repo.get_log_by_id(mission_log_id)
            if not mission_log:
                logger.error(f"Mission log {mission_log_id} not found")
                return {
                    "success": False,
                    "error": "Mission log not found"
                }

            # 사용자 권한 확인
            if mission_log['user_id'] != str(user_id):
                logger.warning(f"User {user_id} attempted to submit mission log {mission_log_id} belonging to another user")
                return {
                    "success": False,
                    "error": "Unauthorized: This mission does not belong to you"
                }

            # 미션 상태 확인
            if mission_log['status'] == 'COMPLETED':
                logger.info(f"Mission log {mission_log_id} already completed")
                return {
                    "success": False,
                    "error": "Mission already completed"
                }

            # 미션 상태를 PENDING_VERIFICATION으로 변경
            await self.mission_log_repo.update_log(
                mission_log_id,
                {"status": "PENDING_VERIFICATION"}
            )

            logger.info(f"Starting RPA submission for mission log {mission_log_id}")

            # 미션 템플릿 조회하여 RPA 설정 확인
            template = await self.mission_template_repo.get_template_by_id(
                mission_log['mission_template_id']
            )

            if not template:
                logger.error(f"Mission template not found for log {mission_log_id}")
                return {
                    "success": False,
                    "error": "Mission template not found"
                }

            # Campaign 조회 (RPA 폼 설정 포함)
            campaign = await self.campaign_repo.get_campaign_by_id(template['campaign_id'])

            if not campaign:
                logger.error(f"Campaign not found for template {template['id']}")
                return {
                    "success": False,
                    "error": "Campaign not found"
                }

            # Deprecated: 2025-01-22 - Playwright RPA removed, use WebView RPA instead
            # TODO: WebView RPA로 대체 - Frontend에서 WebView를 통해 사용자가 직접 제출
            # RPA 실행 방식 결정
            rpa_result = None

            logger.info("RPA auto-submission disabled. Users should submit via WebView.")
            # Manual submission via WebView - no automatic RPA execution
            rpa_result = {
                "success": False,
                "error": "Automatic RPA submission is deprecated. Please use WebView submission.",
                "message": "WebView에서 직접 제출해주세요."
            }

            # # 1. 하이브리드 RPA 사용 (campaign에 rpa_site_config_id와 rpa_form_config가 있으면)
            # if campaign.get('rpa_site_config_id') and campaign.get('rpa_form_config'):
            #     logger.info(f"Using hybrid RPA with site_config_id: {campaign['rpa_site_config_id']}")

            #     # RPA 사이트 설정 조회 (로그인용)
            #     site_config = await self.rpa_config_repo.get_by_id(
            #         campaign['rpa_site_config_id']
            #     )

            #     if not site_config:
            #         logger.error(f"RPA site config not found: {campaign['rpa_site_config_id']}")
            #         return {
            #             "success": False,
            #             "error": "RPA site configuration not found"
            #         }

            #     # 하이브리드 RPA 실행 (로그인 공유 + 폼 개별)
            #     rpa_result = await submit_with_hybrid_config(
            #         campaign_data=campaign,  # rpa_form_config, rpa_field_mapping 등 포함
            #         site_config=site_config,  # login_config, login_selector_strategies 등 포함
            #         submission_data=submission_data,
            #         credentials=credentials
            #     )

            # # 2. 레거시 RPA 사용 (기존 방식 - 하위 호환성)
            # else:
            #     logger.info("Using legacy RPA (submit_eco_mileage_form)")
            #     rpa_result = await submit_eco_mileage_form(submission_data, credentials)

            # RPA 결과에 따라 미션 로그 업데이트
            if rpa_result.get('success'):
                # 성공: COMPLETED 상태로 변경
                updated_log = await self.mission_log_repo.update_log(
                    mission_log_id,
                    {
                        "status": "COMPLETED",
                        "completed_at": datetime.utcnow().isoformat(),
                        "proof_data": {
                            "rpa_result": rpa_result,
                            "submission_data": submission_data,
                            "submitted_at": datetime.utcnow().isoformat()
                        }
                    }
                )

                logger.info(f"Mission log {mission_log_id} marked as COMPLETED")

                # 포인트 지급
                reward_points = template.get('reward_points', 0)
                if reward_points > 0:
                    logger.info(f"Awarding {reward_points} points to user {user_id}")

                    # 1. profiles.total_points 업데이트
                    updated_user = await self.user_repo.add_points(user_id, reward_points)

                    # 2. point_log 기록 생성
                    await self.point_log_repo.create_point_log(
                        user_id=user_id,
                        point=reward_points,
                        description=f"Mission completed: {template.get('title', 'Unknown mission')}"
                    )

                    if updated_user:
                        logger.info(f"Points awarded successfully. New total: {updated_user.get('total_points', 0)}")
                    else:
                        logger.warning(f"Failed to update user points for user {user_id}")

                return {
                    "success": True,
                    "message": "Mission submitted successfully via RPA",
                    "rpa_result": rpa_result,
                    "mission_log": updated_log,
                    "points_awarded": reward_points
                }
            else:
                # 실패: FAILED 상태로 변경
                updated_log = await self.mission_log_repo.update_log(
                    mission_log_id,
                    {
                        "status": "FAILED",
                        "proof_data": {
                            "rpa_result": rpa_result,
                            "error": rpa_result.get('error'),
                            "attempted_at": datetime.utcnow().isoformat()
                        }
                    }
                )

                logger.error(f"RPA submission failed for mission log {mission_log_id}: {rpa_result.get('error')}")

                return {
                    "success": False,
                    "message": "RPA submission failed",
                    "rpa_result": rpa_result,
                    "mission_log": updated_log
                }

        except Exception as e:
            logger.error(f"Error in submit_mission_with_rpa: {str(e)}", exc_info=True)

            # 에러 발생 시 FAILED로 표시
            try:
                await self.mission_log_repo.update_log(
                    mission_log_id,
                    {
                        "status": "FAILED",
                        "proof_data": {
                            "error": str(e),
                            "error_type": "service_error",
                            "attempted_at": datetime.utcnow().isoformat()
                        }
                    }
                )
            except Exception as update_error:
                logger.error(f"Failed to update mission log after error: {str(update_error)}")

            return {
                "success": False,
                "error": f"Service error: {str(e)}"
            }

    async def get_user_campaign_progress(
        self,
        user_id: UUID,
        campaign_id: int
    ) -> Dict[str, Any]:
        """
        사용자의 캠페인 진행 상황 조회

        Parameters:
        -----------
        user_id : UUID
            사용자 ID
        campaign_id : int
            캠페인 ID

        Returns:
        --------
        Dict[str, Any]
            캠페인 진행 상황 정보
        """
        try:
            # 캠페인의 미션 템플릿 조회
            templates = await self.mission_template_repo.get_by_campaign_id(campaign_id)

            # 각 템플릿에 대한 사용자의 로그 조회
            mission_progress = []
            total_missions = len(templates)
            completed_missions = 0
            total_points_earned = 0

            for template in templates:
                log = await self.mission_log_repo.get_by_user_and_template(
                    user_id,
                    template['id']
                )

                progress_item = {
                    "mission_template": template,
                    "status": log['status'] if log else "NOT_STARTED",
                    "log": log
                }

                mission_progress.append(progress_item)

                if log and log['status'] == 'COMPLETED':
                    completed_missions += 1
                    total_points_earned += template.get('reward_points', 0)

            return {
                "campaign_id": campaign_id,
                "total_missions": total_missions,
                "completed_missions": completed_missions,
                "in_progress_missions": total_missions - completed_missions,
                "completion_rate": (completed_missions / total_missions * 100) if total_missions > 0 else 0,
                "total_points_earned": total_points_earned,
                "missions": mission_progress
            }

        except Exception as e:
            logger.error(f"Error getting campaign progress: {str(e)}", exc_info=True)
            return {
                "success": False,
                "error": f"Failed to retrieve campaign progress: {str(e)}"
            }

    async def retry_failed_mission(
        self,
        user_id: UUID,
        mission_log_id: int
    ) -> Dict[str, Any]:
        """
        실패한 미션 재시도

        Parameters:
        -----------
        user_id : UUID
            사용자 ID
        mission_log_id : int
            미션 로그 ID

        Returns:
        --------
        Dict[str, Any]
            업데이트 결과
        """
        try:
            # 미션 로그 조회
            mission_log = await self.mission_log_repo.get_log_by_id(mission_log_id)
            if not mission_log:
                return {
                    "success": False,
                    "error": "Mission log not found"
                }

            # 권한 확인
            if mission_log['user_id'] != str(user_id):
                return {
                    "success": False,
                    "error": "Unauthorized"
                }

            # FAILED 상태인지 확인
            if mission_log['status'] != 'FAILED':
                return {
                    "success": False,
                    "error": "Can only retry failed missions"
                }

            # IN_PROGRESS로 상태 변경
            updated_log = await self.mission_log_repo.update_log(
                mission_log_id,
                {"status": "IN_PROGRESS"}
            )

            logger.info(f"Mission log {mission_log_id} status changed to IN_PROGRESS for retry")

            return {
                "success": True,
                "message": "Mission reset for retry",
                "mission_log": updated_log
            }

        except Exception as e:
            logger.error(f"Error retrying mission: {str(e)}", exc_info=True)
            return {
                "success": False,
                "error": f"Failed to retry mission: {str(e)}"
            }
