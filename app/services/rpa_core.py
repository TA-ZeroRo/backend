"""RPA Core Logic - Automated Form Submission using Playwright"""
import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional
from playwright.async_api import async_playwright, Browser, Page, TimeoutError as PlaywrightTimeout

# 로깅 설정
logger = logging.getLogger(__name__)

# 환경변수로 headless 모드 제어 (기본값: True)
HEADLESS_MODE = os.getenv("RPA_HEADLESS", "true").lower() == "true"
SLOW_MO = int(os.getenv("RPA_SLOW_MO", "0"))  # 밀리초 단위 딜레이
ENABLE_SCREENSHOTS = os.getenv("RPA_SCREENSHOTS", "false").lower() == "true"
SCREENSHOT_DIR = Path("logs/screenshots")

# RPA 대상 URL 설정 (환경변수 또는 기본값)
# 테스트용 Mock HTML 사용: RPA_MODE=mock
# 실제 사이트 사용: RPA_MODE=production
RPA_MODE = os.getenv("RPA_MODE", "production")
MOCK_HTML_PATH = Path(__file__).parent.parent.parent / "tests" / "fixtures" / "mock_eco_form.html"


async def submit_eco_mileage_form(
    submission_data: dict,
    credentials: dict
) -> dict:
    """
    에코마일리지 폼 자동 제출 RPA 함수

    이 함수는 headless Chromium 브라우저를 사용하여 외부 웹사이트에 자동으로 로그인하고
    제공된 데이터를 사용하여 폼을 제출합니다.

    Parameters:
    -----------
    submission_data : dict
        제출할 폼 데이터. 키는 input 필드의 name 속성과 일치해야 함.
        예시: {
            "full_name": "홍길동",
            "email": "hong@example.com",
            "phone": "010-1234-5678",
            "address": "서울시 강남구",
            "activity_description": "재활용 분리수거 실천"
        }

    credentials : dict
        로그인 인증 정보
        예시: {
            "username": "user@example.com",
            "password": "password123"
        }

    Returns:
    --------
    dict
        작업 결과를 담은 딕셔너리
        성공: {"success": True, "message": "Successfully submitted."}
        실패: {"success": False, "error": "Error message"}

    Raises:
    -------
    이 함수는 예외를 발생시키지 않고 항상 결과 딕셔너리를 반환합니다.
    모든 예외는 내부에서 처리되며, 브라우저는 항상 정리됩니다.

    Example:
    --------
    >>> submission_data = {
    ...     "full_name": "홍길동",
    ...     "email": "hong@example.com",
    ...     "phone": "010-1234-5678"
    ... }
    >>> credentials = {
    ...     "username": "user@example.com",
    ...     "password": "password123"
    ... }
    >>> result = await submit_eco_mileage_form(submission_data, credentials)
    >>> print(result)
    {"success": True, "message": "Successfully submitted."}
    """
    browser: Optional[Browser] = None
    page: Optional[Page] = None

    try:
        logger.info("Starting RPA automation for eco-mileage form submission")

        # Step 0: Early validation - Check credentials before launching browser
        if not credentials.get('username') or not credentials.get('password'):
            logger.error("Missing username or password in credentials")
            return {
                "success": False,
                "error": "Missing username or password in credentials"
            }

        # Validate submission_data
        if not submission_data:
            logger.error("submission_data is empty")
            return {
                "success": False,
                "error": "No submission data provided"
            }

        # Step 1: Launch headless Chromium browser
        async with async_playwright() as playwright:
            logger.debug(f"Launching Chromium browser (headless={HEADLESS_MODE}, slow_mo={SLOW_MO}ms)")
            browser = await playwright.chromium.launch(
                headless=HEADLESS_MODE,
                slow_mo=SLOW_MO,
                args=[
                    '--no-sandbox',
                    '--disable-setuid-sandbox',
                    '--disable-dev-shm-usage',
                    '--disable-accelerated-2d-canvas',
                    '--disable-gpu'
                ]
            )

            # Create screenshots directory if enabled
            if ENABLE_SCREENSHOTS:
                SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                screenshot_prefix = f"rpa_{timestamp}"
                logger.debug(f"Screenshots will be saved to {SCREENSHOT_DIR}/{screenshot_prefix}_*.png")

            # Create a new browser context with viewport
            context = await browser.new_context(
                viewport={'width': 1920, 'height': 1080},
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                record_video_dir=str(SCREENSHOT_DIR / "videos") if ENABLE_SCREENSHOTS else None
            )

            page = await context.new_page()

            # Step 2: Navigate to login page
            login_url = "file:///C:/Users/goodj/Desktop/TA-ZeroRo/backend/tests/fixtures/mock_eco_form.html"
            logger.info(f"Navigating to login page: {login_url}")
            await page.goto(login_url, wait_until='networkidle', timeout=30000)

            if ENABLE_SCREENSHOTS:
                await page.screenshot(path=str(SCREENSHOT_DIR / f"{screenshot_prefix}_01_login_page.png"))
                logger.debug("Screenshot saved: 01_login_page.png")

            # Step 3: Perform login
            logger.info("Attempting to log in")

            # Fill login form
            await page.fill('#username', credentials['username'])
            await page.fill('#password', credentials['password'])

            # Click login button and wait for navigation
            logger.debug("Clicking login button")

            if ENABLE_SCREENSHOTS:
                await page.screenshot(path=str(SCREENSHOT_DIR / f"{screenshot_prefix}_02_before_login.png"))
                logger.debug("Screenshot saved: 02_before_login.png")

            # Mock HTML은 실제 navigation이 없으므로 조건부 처리
            if "file:///" in login_url:
                # Mock mode: JavaScript로 페이지 전환하므로 navigation 없음
                await page.click('button[type="submit"]')
                await page.wait_for_timeout(1000)  # JavaScript 실행 대기
            else:
                # Production mode: 실제 페이지 이동
                async with page.expect_navigation(wait_until='networkidle', timeout=30000):
                    await page.click('button[type="submit"]')

            # Check if login was successful (look for error messages)
            if ENABLE_SCREENSHOTS:
                await page.screenshot(path=str(SCREENSHOT_DIR / f"{screenshot_prefix}_03_after_login.png"))
                logger.debug("Screenshot saved: 03_after_login.png")

            error_selector = '.login-error, .alert-danger, .error-message'
            if await page.locator(error_selector).count() > 0:
                error_text = await page.locator(error_selector).first.text_content()
                logger.error(f"Login failed: {error_text}")

                if ENABLE_SCREENSHOTS:
                    await page.screenshot(path=str(SCREENSHOT_DIR / f"{screenshot_prefix}_ERROR_login_failed.png"))

                return {
                    "success": False,
                    "error": f"Login failed: {error_text}"
                }

            logger.info("Login successful")

            # Step 4: Navigate to application page
            # Mock HTML은 이미 같은 페이지에 신청 폼이 있으므로 이동 불필요
            if "file:///" not in login_url:
                apply_url = login_url.replace("/login", "/apply")
                logger.info(f"Navigating to application page: {apply_url}")
                await page.goto(apply_url, wait_until='networkidle', timeout=30000)
            else:
                logger.info("Mock mode: Application form is on the same page, skipping navigation")

            if ENABLE_SCREENSHOTS:
                await page.screenshot(path=str(SCREENSHOT_DIR / f"{screenshot_prefix}_04_apply_page.png"))
                logger.debug("Screenshot saved: 04_apply_page.png")

            # Step 5: Fill application form
            logger.info("Filling application form")

            # Fill each field in the submission data
            for field_name, field_value in submission_data.items():
                selector = f'input[name="{field_name}"], textarea[name="{field_name}"], select[name="{field_name}"]'

                try:
                    # Check if element exists
                    element = page.locator(selector)
                    if await element.count() == 0:
                        logger.warning(f"Field '{field_name}' not found, skipping")
                        continue

                    # Fill the field
                    logger.debug(f"Filling field: {field_name}")
                    await element.first.fill(str(field_value))

                except Exception as field_error:
                    logger.warning(f"Error filling field '{field_name}': {str(field_error)}")
                    # Continue with other fields even if one fails
                    continue

            # Step 6: Submit the form
            logger.info("Submitting the form")

            if ENABLE_SCREENSHOTS:
                await page.screenshot(path=str(SCREENSHOT_DIR / f"{screenshot_prefix}_05_before_submit.png"))
                logger.debug("Screenshot saved: 05_before_submit.png")

            submit_button = page.locator('#submit-button')

            if await submit_button.count() == 0:
                logger.error("Submit button not found")

                if ENABLE_SCREENSHOTS:
                    await page.screenshot(path=str(SCREENSHOT_DIR / f"{screenshot_prefix}_ERROR_no_submit_button.png"))

                return {
                    "success": False,
                    "error": "Submit button not found on the page"
                }

            # Click submit and wait for response
            await submit_button.click()

            # Wait for either success message or error message
            await page.wait_for_timeout(2000)  # Brief wait for page to update

            if ENABLE_SCREENSHOTS:
                await page.screenshot(path=str(SCREENSHOT_DIR / f"{screenshot_prefix}_06_after_submit.png"))
                logger.debug("Screenshot saved: 06_after_submit.png")

            # Step 7: Check for success message
            success_selector = '.success-message'
            logger.debug("Checking for success message")

            if await page.locator(success_selector).count() > 0:
                success_text = await page.locator(success_selector).first.text_content()
                logger.info(f"Form submission successful: {success_text}")

                if ENABLE_SCREENSHOTS:
                    await page.screenshot(path=str(SCREENSHOT_DIR / f"{screenshot_prefix}_SUCCESS_final.png"))
                    logger.debug("Screenshot saved: SUCCESS_final.png")

                return {
                    "success": True,
                    "message": success_text.strip() if success_text else "Successfully submitted."
                }
            else:
                # Check for error messages
                form_error_selector = '.form-error, .alert-danger, .error'
                if await page.locator(form_error_selector).count() > 0:
                    error_text = await page.locator(form_error_selector).first.text_content()
                    logger.error(f"Form submission failed: {error_text}")

                    if ENABLE_SCREENSHOTS:
                        await page.screenshot(path=str(SCREENSHOT_DIR / f"{screenshot_prefix}_ERROR_form_validation.png"))

                    return {
                        "success": False,
                        "error": f"Form validation error: {error_text}"
                    }
                else:
                    logger.warning("No success or error message found after submission")

                    if ENABLE_SCREENSHOTS:
                        await page.screenshot(path=str(SCREENSHOT_DIR / f"{screenshot_prefix}_ERROR_no_confirmation.png"))

                    return {
                        "success": False,
                        "error": "Form submitted but no confirmation received"
                    }

    except PlaywrightTimeout as timeout_error:
        logger.error(f"Timeout error during RPA execution: {str(timeout_error)}", exc_info=True)

        if ENABLE_SCREENSHOTS and page:
            try:
                await page.screenshot(path=str(SCREENSHOT_DIR / f"rpa_ERROR_timeout.png"))
            except:
                pass

        return {
            "success": False,
            "error": f"Timeout: {str(timeout_error)}"
        }

    except Exception as e:
        logger.error(f"Unexpected error during RPA execution: {str(e)}", exc_info=True)

        if ENABLE_SCREENSHOTS and page:
            try:
                await page.screenshot(path=str(SCREENSHOT_DIR / f"rpa_ERROR_unexpected.png"))
            except:
                pass

        return {
            "success": False,
            "error": f"Unexpected error: {str(e)}"
        }

    finally:
        # Step 8: Cleanup - Always close browser
        if browser:
            try:
                logger.debug("Closing browser")
                await browser.close()
                logger.info("Browser closed successfully")
            except Exception as cleanup_error:
                logger.error(f"Error closing browser: {str(cleanup_error)}", exc_info=True)


# ===== 보조 함수들 =====

async def validate_form_fields(
    page: Page,
    required_fields: list[str]
) -> tuple[bool, Optional[str]]:
    """
    폼의 필수 필드가 모두 존재하는지 검증

    Parameters:
    -----------
    page : Page
        Playwright Page 객체
    required_fields : list[str]
        검증할 필수 필드 name 목록

    Returns:
    --------
    tuple[bool, Optional[str]]
        (성공 여부, 에러 메시지)
    """
    missing_fields = []

    for field_name in required_fields:
        selector = f'input[name="{field_name}"], textarea[name="{field_name}"], select[name="{field_name}"]'
        if await page.locator(selector).count() == 0:
            missing_fields.append(field_name)

    if missing_fields:
        error_msg = f"Missing required fields: {', '.join(missing_fields)}"
        return False, error_msg

    return True, None


async def take_screenshot_on_error(
    page: Page,
    filename: str = "error_screenshot.png"
) -> Optional[str]:
    """
    에러 발생 시 스크린샷 저장 (디버깅용)

    Parameters:
    -----------
    page : Page
        Playwright Page 객체
    filename : str
        저장할 파일명

    Returns:
    --------
    Optional[str]
        저장된 파일 경로 또는 None
    """
    try:
        screenshot_path = f"/tmp/{filename}"
        await page.screenshot(path=screenshot_path, full_page=True)
        logger.info(f"Screenshot saved to {screenshot_path}")
        return screenshot_path
    except Exception as e:
        logger.error(f"Failed to save screenshot: {str(e)}")
        return None


# ===== 새로운 설정 기반 RPA 함수 =====

async def submit_with_hybrid_config(
    campaign_data: dict,
    site_config: dict,
    submission_data: dict,
    credentials: dict
) -> dict:
    """
    하이브리드 RPA 제출 함수 (로그인 공유 + 폼 개별)

    로그인 설정: rpa_site_configs (공유)
    폼 설정: campaigns (개별)

    Parameters:
    -----------
    campaign_data : dict
        Campaign 데이터 (rpa_form_url, rpa_form_config, rpa_field_mapping 등)
    site_config : dict
        사이트 로그인 설정 (rpa_site_configs 레코드)
    submission_data : dict
        제출할 데이터
        예: {"user_name": "홍길동", "user_birth": "900101", ...}
    credentials : dict
        로그인 인증 정보
        예: {"username": "user@example.com", "password": "password123"}

    Returns:
    --------
    dict
        {"success": True, "message": "..."} 또는 {"success": False, "error": "..."}

    Example:
    --------
    >>> result = await submit_with_hybrid_config(
    ...     campaign_data={
    ...         "rpa_form_url": "https://eco.seoul.go.kr/apply",
    ...         "rpa_form_config": {"selectors": {...}},
    ...         "rpa_field_mapping": {"user_name": "name_input"}
    ...     },
    ...     site_config={
    ...         "login_url": "https://eco.seoul.go.kr/login",
    ...         "login_config": {"selectors": {...}}
    ...     },
    ...     submission_data={"user_name": "홍길동"},
    ...     credentials={"username": "test@example.com", "password": "test123"}
    ... )
    >>> print(result)
    {"success": True, "message": "Successfully submitted."}
    """
    from app.services.rpa_adapters.base import SelfHealingAdapter

    browser: Optional[Browser] = None

    try:
        logger.info(f"Starting hybrid RPA for site: {site_config.get('site_name')}")

        # Step 1: Validate inputs
        if not credentials.get('username') or not credentials.get('password'):
            logger.error("Missing username or password in credentials")
            return {
                "success": False,
                "error": "Missing username or password in credentials"
            }

        if not submission_data:
            logger.error("submission_data is empty")
            return {
                "success": False,
                "error": "No submission data provided"
            }

        if not campaign_data.get('rpa_form_config'):
            logger.error("Missing rpa_form_config in campaign_data")
            return {
                "success": False,
                "error": "Campaign RPA form configuration is missing"
            }

        # Step 2: Launch browser
        async with async_playwright() as playwright:
            logger.debug(f"Launching Chromium browser (headless={HEADLESS_MODE})")
            browser = await playwright.chromium.launch(
                headless=HEADLESS_MODE,
                slow_mo=SLOW_MO,
                args=[
                    '--no-sandbox',
                    '--disable-setuid-sandbox',
                    '--disable-dev-shm-usage',
                    '--disable-accelerated-2d-canvas',
                    '--disable-gpu'
                ]
            )

            # Create browser context
            context = await browser.new_context(
                viewport={'width': 1920, 'height': 1080},
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            )

            page = await context.new_page()

            # Step 3: Initialize Self-Healing Adapter (하이브리드)
            adapter = SelfHealingAdapter(
                page=page,
                login_config=site_config.get('login_config', {}),
                login_strategies=site_config.get('login_selector_strategies'),
                form_config=campaign_data.get('rpa_form_config', {}),
                form_strategies=campaign_data.get('rpa_form_selector_strategies'),
                field_mapping=campaign_data.get('rpa_field_mapping', {})
            )

            # Step 4: Login (공통 설정 사용)
            logger.info("Attempting login")
            await page.goto(site_config['login_url'])
            await page.wait_for_load_state('networkidle')

            login_success = await adapter.login(credentials)

            if not login_success:
                logger.error("Login failed")
                return {
                    "success": False,
                    "error": "Login failed - check credentials or site configuration"
                }

            # Step 5: Navigate to form (Campaign별 URL)
            form_url = campaign_data.get('rpa_form_url')
            if form_url:
                logger.info(f"Navigating to form: {form_url}")
                await page.goto(form_url)
                await page.wait_for_load_state('networkidle')
            else:
                logger.debug("No form_url specified, assuming form is on current page")

            # Step 5.5: Open modal if needed (wait for modal trigger button and click)
            modal_trigger = campaign_data.get('rpa_modal_trigger')
            if modal_trigger:
                logger.info(f"Opening modal with trigger: {modal_trigger}")
                try:
                    trigger_button = page.locator(modal_trigger)
                    await trigger_button.click()
                    # Wait for modal to appear
                    await page.wait_for_timeout(1000)
                    logger.info("Modal opened successfully")
                except Exception as e:
                    logger.warning(f"Failed to open modal: {e}")

            # Step 6: Fill form (Campaign별 설정 사용)
            logger.info("Filling form")
            fill_success = await adapter.fill_form(submission_data)

            if not fill_success:
                logger.warning("No fields were filled")
                return {
                    "success": False,
                    "error": "Failed to fill form - check field mapping configuration"
                }

            # Step 7: Submit form
            result = await adapter.submit_form()

            logger.info(f"Hybrid RPA completed: {result}")

            return result

    except Exception as e:
        logger.error(f"Unexpected error during hybrid RPA execution: {str(e)}", exc_info=True)
        return {
            "success": False,
            "error": f"Unexpected error: {str(e)}"
        }

    finally:
        # Cleanup
        if browser:
            try:
                logger.debug("Closing browser")
                await browser.close()
                logger.info("Browser closed successfully")
            except Exception as cleanup_error:
                logger.error(f"Error closing browser: {str(cleanup_error)}", exc_info=True)
