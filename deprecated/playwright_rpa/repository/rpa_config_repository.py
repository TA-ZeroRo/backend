"""RPA Config Repository - RPA 사이트 설정 관리"""
from typing import List, Dict, Any, Optional
from app.repository.base_repository import BaseRepository
import logging

logger = logging.getLogger(__name__)


class RPAConfigRepository(BaseRepository):
    """RPA 사이트 설정 관련 데이터베이스 작업을 처리하는 Repository"""

    TABLE_NAME = "rpa_site_configs"

    async def get_by_site_code(self, site_code: str) -> Optional[Dict[str, Any]]:
        """
        사이트 코드로 RPA 설정 조회

        Parameters:
        -----------
        site_code : str
            사이트 코드 (예: 'seoul_ecomileage')

        Returns:
        --------
        Optional[Dict[str, Any]]
            RPA 설정 또는 None
        """
        try:
            response = (
                self.supabase
                .table(self.TABLE_NAME)
                .select("*")
                .eq("site_code", site_code)
                .eq("is_active", True)
                .single()
                .execute()
            )

            if response.data:
                logger.debug(f"Found RPA config for site_code: {site_code}")
                return response.data

            return None

        except Exception as e:
            logger.error(f"Error fetching RPA config for {site_code}: {e}")
            return None

    async def get_by_id(self, config_id: int) -> Optional[Dict[str, Any]]:
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
        return await self.find_by_id(self.TABLE_NAME, str(config_id))

    async def get_all_active(self) -> List[Dict[str, Any]]:
        """
        활성화된 모든 RPA 설정 조회

        Returns:
        --------
        List[Dict[str, Any]]
            RPA 설정 목록
        """
        return await self.find_all(self.TABLE_NAME, filters={"is_active": True})

    async def create_config(self, config_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        새 RPA 설정 생성

        Parameters:
        -----------
        config_data : Dict[str, Any]
            {
                "site_code": "...",
                "site_name": "...",
                "base_url": "...",
                "login_url": "...",
                "form_url": "..." or None,
                "login_config": {...},
                "form_config": {...},
                "selector_strategies": {...},
                "field_mapping": {...}
            }

        Returns:
        --------
        Optional[Dict[str, Any]]
            생성된 RPA 설정
        """
        logger.info(f"Creating RPA config for site: {config_data.get('site_code')}")
        return await self.create(self.TABLE_NAME, config_data)

    async def update_config(
        self,
        config_id: int,
        update_data: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
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
        Optional[Dict[str, Any]]
            업데이트된 RPA 설정
        """
        logger.info(f"Updating RPA config ID: {config_id}")
        return await self.update(self.TABLE_NAME, str(config_id), update_data)

    async def update_selector_strategy(
        self,
        site_code: str,
        element_key: str,
        new_strategy: Dict[str, Any]
    ) -> bool:
        """
        특정 요소의 셀렉터 전략 추가/업데이트 (Self-Healing 개선)

        Parameters:
        -----------
        site_code : str
            사이트 코드
        element_key : str
            요소 키 (예: 'username_input')
        new_strategy : Dict[str, Any]
            새 전략 (예: {"selector": "#newId", "priority": 1, "method": "id"})

        Returns:
        --------
        bool
            성공 여부
        """
        try:
            # 기존 설정 조회
            config = await self.get_by_site_code(site_code)

            if not config:
                logger.error(f"RPA config not found for site_code: {site_code}")
                return False

            # selector_strategies 업데이트
            selector_strategies = config.get('selector_strategies', {})
            element_strategies = selector_strategies.get(element_key, [])

            # 새 전략 추가
            element_strategies.append(new_strategy)

            # priority로 정렬
            element_strategies.sort(key=lambda x: x.get('priority', 999))

            selector_strategies[element_key] = element_strategies

            # DB 업데이트
            await self.update_config(
                config['id'],
                {"selector_strategies": selector_strategies}
            )

            logger.info(
                f"Added selector strategy for {site_code}.{element_key}: {new_strategy}"
            )

            return True

        except Exception as e:
            logger.error(f"Error updating selector strategy: {e}")
            return False

    async def deactivate_config(self, config_id: int) -> bool:
        """
        RPA 설정 비활성화

        Parameters:
        -----------
        config_id : int
            설정 ID

        Returns:
        --------
        bool
            성공 여부
        """
        result = await self.update_config(config_id, {"is_active": False})
        return result is not None
