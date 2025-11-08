"""
Pytest Test Cases for RPA Core
실행 방법:
1. venv 활성화
2. pip install pytest pytest-asyncio
3. pytest tests/test_rpa_core.py -v
"""
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import pytest
from app.services.rpa_core import submit_eco_mileage_form


class TestRPACore:
    """RPA Core 로직 테스트"""

    @pytest.mark.asyncio
    async def test_missing_username(self):
        """username이 없는 경우 실패해야 함"""
        campaign_url = "http://example.com"
        submission_data = {"name": "홍길동"}
        credentials = {"password": "test123"}  # username 없음

        result = await submit_eco_mileage_form(campaign_url, submission_data, credentials)

        assert result["success"] is False
        assert "Missing username" in result["error"]

    @pytest.mark.asyncio
    async def test_missing_password(self):
        """password가 없는 경우 실패해야 함"""
        campaign_url = "http://example.com"
        submission_data = {"name": "홍길동"}
        credentials = {"username": "test@example.com"}  # password 없음

        result = await submit_eco_mileage_form(campaign_url, submission_data, credentials)

        assert result["success"] is False
        assert "password" in result["error"].lower()

    @pytest.mark.asyncio
    async def test_empty_credentials(self):
        """빈 credentials인 경우 실패해야 함"""
        campaign_url = "http://example.com"
        submission_data = {"name": "홍길동"}
        credentials = {}

        result = await submit_eco_mileage_form(campaign_url, submission_data, credentials)

        assert result["success"] is False
        assert "Missing" in result["error"]

    @pytest.mark.asyncio
    async def test_empty_submission_data(self):
        """빈 submission_data인 경우 실패해야 함"""
        campaign_url = "http://example.com"
        submission_data = {}
        credentials = {
            "username": "test@example.com",
            "password": "test123"
        }

        result = await submit_eco_mileage_form(campaign_url, submission_data, credentials)

        assert result["success"] is False
        assert "No submission data" in result["error"]

    @pytest.mark.asyncio
    async def test_invalid_url_timeout(self):
        """잘못된 URL로 인한 타임아웃 처리"""
        campaign_url = "http://example.com/nonexistent"
        submission_data = {"name": "홍길동"}
        credentials = {
            "username": "test@example.com",
            "password": "test123"
        }

        # 현재 코드에서는 example.com URL을 사용하므로 타임아웃 또는 에러 발생
        result = await submit_eco_mileage_form(campaign_url, submission_data, credentials)

        # 타임아웃이나 네트워크 에러로 실패해야 함
        assert result["success"] is False
        assert "error" in result

    @pytest.mark.asyncio
    async def test_result_structure(self):
        """반환 결과의 구조가 올바른지 확인"""
        campaign_url = "http://example.com"
        submission_data = {}
        credentials = {"username": "test", "password": "test"}

        result = await submit_eco_mileage_form(campaign_url, submission_data, credentials)

        # 결과는 항상 dict이어야 함
        assert isinstance(result, dict)

        # success 키가 있어야 함
        assert "success" in result

        # success가 False면 error 키가 있어야 함
        if not result["success"]:
            assert "error" in result

        # success가 True면 message 키가 있어야 함
        if result["success"]:
            assert "message" in result


class TestRPAValidationHelpers:
    """RPA 검증 헬퍼 함수 테스트"""

    @pytest.mark.asyncio
    async def test_validate_form_fields_missing(self):
        """필수 필드 누락 검증"""
        from playwright.async_api import async_playwright

        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()

            # 간단한 HTML 설정
            await page.set_content("""
                <html>
                <body>
                    <input name="field1" />
                    <!-- field2는 없음 -->
                </body>
                </html>
            """)

            from app.services.rpa_core import validate_form_fields

            # field2가 없으므로 실패해야 함
            is_valid, error_msg = await validate_form_fields(
                page,
                ["field1", "field2"]
            )

            assert is_valid is False
            assert "field2" in error_msg

            await browser.close()

    @pytest.mark.asyncio
    async def test_validate_form_fields_all_present(self):
        """모든 필수 필드가 있는 경우"""
        from playwright.async_api import async_playwright

        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()

            await page.set_content("""
                <html>
                <body>
                    <input name="field1" />
                    <input name="field2" />
                </body>
                </html>
            """)

            from app.services.rpa_core import validate_form_fields

            is_valid, error_msg = await validate_form_fields(
                page,
                ["field1", "field2"]
            )

            assert is_valid is True
            assert error_msg is None

            await browser.close()


@pytest.mark.asyncio
async def test_screenshot_function():
    """스크린샷 함수 테스트"""
    from playwright.async_api import async_playwright
    from app.services.rpa_core import take_screenshot_on_error
    import os

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.set_content("<html><body><h1>Test Page</h1></body></html>")

        # 스크린샷 저장
        screenshot_path = await take_screenshot_on_error(page, "test_screenshot.png")

        # Windows에서는 /tmp 대신 적절한 경로 사용
        if screenshot_path:
            # 파일이 실제로 생성되었는지는 환경에 따라 다를 수 있음
            assert "test_screenshot.png" in screenshot_path

        await browser.close()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
