"""RPA Config Service - RPA 설정 비즈니스 로직"""
import logging
from typing import Dict, Any, Optional, List
from app.repository.rpa_config_repository import RPAConfigRepository

logger = logging.getLogger(__name__)


class RPAConfigService:
    """RPA 설정 관련 비즈니스 로직을 처리하는 Service"""

    def __init__(self):
        self.repo = RPAConfigRepository()

    async def get_config(self, site_code: str) -> Optional[Dict[str, Any]]:
        """
        사이트 코드로 RPA 설정 조회

        Parameters:
        -----------
        site_code : str
            사이트 코드

        Returns:
        --------
        Optional[Dict[str, Any]]
            RPA 설정 또는 None
        """
        config = await self.repo.get_by_site_code(site_code)

        if not config:
            logger.warning(f"RPA config not found for site_code: {site_code}")

        return config

    async def get_config_by_id(self, config_id: int) -> Optional[Dict[str, Any]]:
        """
        ID로 RPA 설정 조회

        Parameters:
        -----------
        config_id : int
            설정 ID

        Returns:
        --------
        Optional[Dict[str, Any]]
            RPA 설정 또는 None
        """
        return await self.repo.get_by_id(config_id)

    async def validate_config(self, config: Dict[str, Any]) -> tuple[bool, Optional[str]]:
        """
        RPA 설정 유효성 검증

        Parameters:
        -----------
        config : Dict[str, Any]
            검증할 RPA 설정

        Returns:
        --------
        tuple[bool, Optional[str]]
            (유효 여부, 에러 메시지)
        """
        # 필수 필드 확인
        required_fields = [
            'site_code',
            'site_name',
            'base_url',
            'login_url',
            'login_config',
            'form_config'
        ]

        for field in required_fields:
            if not config.get(field):
                return False, f"Missing required field: {field}"

        # login_config 구조 확인
        login_config = config.get('login_config', {})
        required_login_selectors = ['username_input', 'password_input', 'submit_button']

        login_selectors = login_config.get('selectors', {})
        for selector_key in required_login_selectors:
            if not login_selectors.get(selector_key):
                return False, f"Missing login selector: {selector_key}"

        # form_config 구조 확인
        form_config = config.get('form_config', {})
        required_form_selectors = ['submit_button']

        form_selectors = form_config.get('selectors', {})
        for selector_key in required_form_selectors:
            if not form_selectors.get(selector_key):
                return False, f"Missing form selector: {selector_key}"

        return True, None

    async def create_config(self, config_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        새 RPA 설정 생성

        Parameters:
        -----------
        config_data : Dict[str, Any]
            RPA 설정 데이터

        Returns:
        --------
        Dict[str, Any]
            {"success": bool, "data": {...}} 또는 {"success": bool, "error": str}
        """
        # 검증
        is_valid, error_msg = await self.validate_config(config_data)

        if not is_valid:
            logger.error(f"Invalid RPA config: {error_msg}")
            return {"success": False, "error": error_msg}

        # 중복 확인
        existing = await self.repo.get_by_site_code(config_data['site_code'])

        if existing:
            logger.error(f"RPA config already exists for site_code: {config_data['site_code']}")
            return {
                "success": False,
                "error": f"Site code '{config_data['site_code']}' already exists"
            }

        # 생성
        try:
            created = await self.repo.create_config(config_data)

            if created:
                logger.info(f"Created RPA config for site: {config_data['site_code']}")
                return {"success": True, "data": created}

            return {"success": False, "error": "Failed to create config"}

        except Exception as e:
            logger.error(f"Error creating RPA config: {e}", exc_info=True)
            return {"success": False, "error": str(e)}

    async def update_config(
        self,
        config_id: int,
        update_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        RPA 설정 업데이트

        Parameters:
        -----------
        config_id : int
            설정 ID
        update_data : Dict[str, Any]
            업데이트할 데이터

        Returns:
        --------
        Dict[str, Any]
            {"success": bool, "data": {...}} 또는 {"success": bool, "error": str}
        """
        try:
            updated = await self.repo.update_config(config_id, update_data)

            if updated:
                logger.info(f"Updated RPA config ID: {config_id}")
                return {"success": True, "data": updated}

            return {"success": False, "error": "Config not found"}

        except Exception as e:
            logger.error(f"Error updating RPA config: {e}", exc_info=True)
            return {"success": False, "error": str(e)}

    async def add_selector_strategy(
        self,
        site_code: str,
        element_key: str,
        selector: str,
        priority: int,
        method: str = "unknown"
    ) -> Dict[str, Any]:
        """
        셀렉터 전략 추가 (Self-Healing 개선)

        Parameters:
        -----------
        site_code : str
            사이트 코드
        element_key : str
            요소 키
        selector : str
            CSS 셀렉터
        priority : int
            우선순위 (낮을수록 먼저 시도)
        method : str
            식별 방법 (id, class, name, xpath 등)

        Returns:
        --------
        Dict[str, Any]
            {"success": bool} 또는 {"success": bool, "error": str}
        """
        new_strategy = {
            "selector": selector,
            "priority": priority,
            "method": method
        }

        success = await self.repo.update_selector_strategy(
            site_code,
            element_key,
            new_strategy
        )

        if success:
            logger.info(
                f"Added selector strategy for {site_code}.{element_key}: "
                f"{selector} (priority={priority})"
            )
            return {"success": True}

        return {"success": False, "error": "Failed to add selector strategy"}
