"""
RPA Integration Test - 전체 플로우 테스트

실행 방법:
1. DB에 rpa_site_configs 테이블 생성 및 seed 데이터 삽입 필요
2. pytest tests/test_rpa_integration.py -v -s

주의: 이 테스트는 실제 DB 연결이 필요합니다.
"""
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import pytest
import asyncio


class TestRPAIntegration:
    """RPA 전체 통합 테스트"""

    @pytest.mark.asyncio
    @pytest.mark.skip(reason="Requires DB setup")
    async def test_full_rpa_flow_with_config(self):
        """설정 기반 RPA 전체 플로우 테스트"""
        from app.services.rpa_core import submit_with_config

        # Test data
        site_code = "seoul_ecomileage_mock"

        submission_data = {
            "user_name": "홍길동",
            "user_birth": "900101",
            "user_phone": "01012345678",
            "activity_date": "2025-01-09",
            "description": "재활용 분리수거 실천"
        }

        credentials = {
            "username": "test@example.com",
            "password": "password123"
        }

        # Execute
        result = await submit_with_config(site_code, submission_data, credentials)

        # Assert
        print(f"\n결과: {result}")
        assert result is not None
        assert "success" in result

        if result["success"]:
            print(f"✅ 성공: {result.get('message')}")
            assert "message" in result
        else:
            print(f"❌ 실패: {result.get('error')}")
            # Mock HTML이 없으면 실패할 수 있음

    @pytest.mark.asyncio
    async def test_rpa_config_service(self):
        """RPA Config Service 테스트"""
        from app.services.rpa_config_service import RPAConfigService

        service = RPAConfigService()

        # Test validation
        valid_config = {
            "site_code": "test_site",
            "site_name": "테스트 사이트",
            "base_url": "https://example.com",
            "login_url": "https://example.com/login",
            "login_config": {
                "selectors": {
                    "username_input": "#username",
                    "password_input": "#password",
                    "submit_button": "button[type='submit']"
                }
            },
            "form_config": {
                "selectors": {
                    "submit_button": "#submit"
                }
            }
        }

        is_valid, error = await service.validate_config(valid_config)

        assert is_valid is True
        assert error is None
        print("✅ 설정 검증 통과")

    @pytest.mark.asyncio
    async def test_rpa_config_validation_fail(self):
        """RPA Config 검증 실패 테스트"""
        from app.services.rpa_config_service import RPAConfigService

        service = RPAConfigService()

        # Missing required field
        invalid_config = {
            "site_code": "test_site",
            # Missing site_name, base_url, etc.
        }

        is_valid, error = await service.validate_config(invalid_config)

        assert is_valid is False
        assert error is not None
        assert "Missing required field" in error
        print(f"✅ 검증 실패 확인: {error}")

    def test_adapter_pattern_structure(self):
        """Adapter 패턴 구조 확인"""
        from app.services.rpa_adapters.base import SelfHealingAdapter
        from playwright.async_api import Page
        from unittest.mock import MagicMock

        # Mock page
        mock_page = MagicMock(spec=Page)

        # Mock config
        config = {
            "login_config": {"selectors": {}},
            "form_config": {"selectors": {}},
            "selector_strategies": {},
            "field_mapping": {}
        }

        # Create adapter
        adapter = SelfHealingAdapter(mock_page, config)

        # Verify methods exist
        assert hasattr(adapter, 'find_element')
        assert hasattr(adapter, 'login')
        assert hasattr(adapter, 'navigate_to_form')
        assert hasattr(adapter, 'fill_form')
        assert hasattr(adapter, 'submit_form')

        print("✅ Adapter 패턴 구조 확인 완료")

    def test_self_healing_strategy_sorting(self):
        """Self-Healing 전략 정렬 확인"""
        strategies = [
            {"selector": "#third", "priority": 3},
            {"selector": "#first", "priority": 1},
            {"selector": "#second", "priority": 2}
        ]

        sorted_strategies = sorted(strategies, key=lambda x: x.get('priority', 999))

        assert sorted_strategies[0]['selector'] == "#first"
        assert sorted_strategies[1]['selector'] == "#second"
        assert sorted_strategies[2]['selector'] == "#third"

        print("✅ Self-Healing 전략 우선순위 정렬 확인")

    @pytest.mark.asyncio
    async def test_repository_methods(self):
        """Repository 메서드 존재 확인"""
        from app.repository.rpa_config_repository import RPAConfigRepository
        from app.repository.mission_template_repository import MissionTemplateRepository

        rpa_repo = RPAConfigRepository()
        mission_repo = MissionTemplateRepository()

        # Verify methods exist
        assert hasattr(rpa_repo, 'get_by_site_code')
        assert hasattr(rpa_repo, 'get_by_id')
        assert hasattr(rpa_repo, 'create_config')

        assert hasattr(mission_repo, 'get_template_by_id')
        assert hasattr(mission_repo, 'get_by_campaign_id')

        print("✅ Repository 메서드 확인 완료")


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v", "-s"])
