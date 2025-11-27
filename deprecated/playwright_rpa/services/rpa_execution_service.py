"""RPA Execution Service - API를 통한 RPA 실행 관리"""
import logging
import time
from typing import Dict, Any
from app.repository.campaign_repository import CampaignRepository
from app.repository.rpa_config_repository import RPAConfigRepository
from app.services.rpa_core import submit_with_hybrid_config

logger = logging.getLogger(__name__)


class RPAExecutionService:
    """RPA 실행을 관리하는 서비스 레이어"""

    def __init__(self):
        self.campaign_repo = CampaignRepository()
        self.rpa_config_repo = RPAConfigRepository()

    async def execute_rpa_for_campaign(
        self,
        campaign_id: int,
        submission_data: Dict[str, Any],
        credentials: Dict[str, str]
    ) -> Dict[str, Any]:
        """
        Campaign ID로 RPA 실행

        Parameters:
        -----------
        campaign_id : int
            실행할 Campaign ID
        submission_data : Dict[str, Any]
            폼에 제출할 데이터 (field_mapping에 정의된 키 사용)
        credentials : Dict[str, str]
            로그인 인증 정보 {"username": "...", "password": "..."}

        Returns:
        --------
        Dict[str, Any]
            {
                "success": bool,
                "message": str,
                "error": str (실패 시),
                "execution_time": float,
                "campaign_id": int
            }
        """
        start_time = time.time()

        logger.info(f"Starting RPA execution for campaign_id={campaign_id}")

        try:
            # 1. Campaign 조회
            campaign = await self.campaign_repo.get_campaign_by_id(campaign_id)

            if not campaign:
                logger.error(f"Campaign not found: campaign_id={campaign_id}")
                return {
                    "success": False,
                    "error": f"Campaign with ID {campaign_id} not found",
                    "execution_time": time.time() - start_time,
                    "campaign_id": campaign_id
                }

            # 2. RPA 설정 검증
            rpa_site_config_id = campaign.get("rpa_site_config_id")

            if not rpa_site_config_id:
                logger.error(f"Campaign {campaign_id} has no RPA site config")
                return {
                    "success": False,
                    "error": f"Campaign {campaign_id} is not configured for RPA",
                    "execution_time": time.time() - start_time,
                    "campaign_id": campaign_id
                }

            # 3. RPA Site Config 조회
            site_config = await self.rpa_config_repo.get_by_id(rpa_site_config_id)

            if not site_config:
                logger.error(f"RPA site config not found: id={rpa_site_config_id}")
                return {
                    "success": False,
                    "error": f"RPA site config with ID {rpa_site_config_id} not found",
                    "execution_time": time.time() - start_time,
                    "campaign_id": campaign_id
                }

            # 4. 필수 필드 검증
            if not campaign.get("rpa_form_config"):
                logger.error(f"Campaign {campaign_id} has no form config")
                return {
                    "success": False,
                    "error": f"Campaign {campaign_id} has no RPA form configuration",
                    "execution_time": time.time() - start_time,
                    "campaign_id": campaign_id
                }

            # 5. Config 데이터 구조화
            campaign_data = {
                "form_url": campaign.get("rpa_form_url"),
                "form_config": campaign.get("rpa_form_config"),
                "form_selector_strategies": campaign.get("rpa_form_selector_strategies"),
                "field_mapping": campaign.get("rpa_field_mapping"),
            }

            site_config_data = {
                "login_url": site_config.get("login_url"),
                "login_config": site_config.get("login_config"),
                "login_selector_strategies": site_config.get("login_selector_strategies"),
            }

            logger.info(f"Configs loaded for campaign_id={campaign_id}, site_code={site_config.get('site_code')}")

            # 6. RPA 실행 (rpa_core의 기존 로직 활용)
            result = await submit_with_hybrid_config(
                campaign_data=campaign_data,
                site_config=site_config_data,
                submission_data=submission_data,
                credentials=credentials
            )

            execution_time = time.time() - start_time

            logger.info(
                f"RPA execution completed for campaign_id={campaign_id}, "
                f"success={result.get('success')}, time={execution_time:.2f}s"
            )

            # 7. 결과 반환 (execution_time과 campaign_id 추가)
            return {
                **result,
                "execution_time": execution_time,
                "campaign_id": campaign_id
            }

        except Exception as e:
            execution_time = time.time() - start_time
            logger.exception(f"RPA execution failed for campaign_id={campaign_id}: {e}")

            return {
                "success": False,
                "error": f"RPA execution failed: {str(e)}",
                "execution_time": execution_time,
                "campaign_id": campaign_id
            }
