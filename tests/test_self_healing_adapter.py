"""
Self-Healing RPA Adapter 테스트

실행 방법:
pytest tests/test_self_healing_adapter.py -v
"""
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import pytest
from unittest.mock import AsyncMock, MagicMock


class TestSelfHealingAdapter:
    """Self-Healing Adapter 로직 테스트"""

    def test_import_adapter(self):
        """Adapter 클래스 import 테스트"""
        from app.services.rpa_adapters.base import SelfHealingAdapter
        assert SelfHealingAdapter is not None

    @pytest.mark.asyncio
    async def test_find_element_with_default_selector(self):
        """기본 셀렉터로 요소 찾기"""
        from app.services.rpa_adapters.base import SelfHealingAdapter

        # Mock page
        mock_page = AsyncMock()
        mock_locator = AsyncMock()
        mock_locator.count = AsyncMock(return_value=1)
        mock_locator.first = MagicMock()
        mock_page.locator = MagicMock(return_value=mock_locator)

        # Config without strategies
        config = {
            "login_config": {
                "selectors": {
                    "username_input": "#username"
                }
            },
            "form_config": {"selectors": {}},
            "selector_strategies": {},
            "field_mapping": {}
        }

        adapter = SelfHealingAdapter(mock_page, config)

        # Execute
        element = await adapter.find_element("username_input", context="login")

        # Assert
        assert element is not None
        mock_page.locator.assert_called_with("#username")

    @pytest.mark.asyncio
    async def test_find_element_with_strategies(self):
        """여러 전략으로 요소 찾기 (Self-Healing)"""
        from app.services.rpa_adapters.base import SelfHealingAdapter

        # Mock page - 첫 번째 셀렉터는 실패, 두 번째 성공
        mock_page = AsyncMock()

        # First selector fails
        mock_locator_fail = AsyncMock()
        mock_locator_fail.count = AsyncMock(return_value=0)

        # Second selector succeeds
        mock_locator_success = AsyncMock()
        mock_locator_success.count = AsyncMock(return_value=1)
        mock_locator_success.first = MagicMock()

        call_count = 0

        def mock_locator_factory(selector):
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                return mock_locator_fail
            return mock_locator_success

        mock_page.locator = MagicMock(side_effect=mock_locator_factory)

        # Config with strategies
        config = {
            "login_config": {"selectors": {}},
            "form_config": {"selectors": {}},
            "selector_strategies": {
                "username_input": [
                    {"selector": "#wrong-id", "priority": 1, "method": "id"},
                    {"selector": "input[name='username']", "priority": 2, "method": "name"}
                ]
            },
            "field_mapping": {}
        }

        adapter = SelfHealingAdapter(mock_page, config)

        # Execute
        element = await adapter.find_element("username_input")

        # Assert - 두 번째 전략으로 찾음
        assert element is not None
        assert call_count == 2

    @pytest.mark.asyncio
    async def test_find_element_all_strategies_fail(self):
        """모든 전략 실패 시 예외 발생"""
        from app.services.rpa_adapters.base import SelfHealingAdapter

        # Mock page - 모든 셀렉터 실패
        mock_page = AsyncMock()
        mock_locator = AsyncMock()
        mock_locator.count = AsyncMock(return_value=0)
        mock_page.locator = MagicMock(return_value=mock_locator)

        config = {
            "login_config": {"selectors": {}},
            "form_config": {"selectors": {}},
            "selector_strategies": {
                "username_input": [
                    {"selector": "#wrong1", "priority": 1},
                    {"selector": "#wrong2", "priority": 2}
                ]
            },
            "field_mapping": {}
        }

        adapter = SelfHealingAdapter(mock_page, config)

        # Execute & Assert
        with pytest.raises(Exception) as exc_info:
            await adapter.find_element("username_input")

        assert "All" in str(exc_info.value)
        assert "strategies failed" in str(exc_info.value)
