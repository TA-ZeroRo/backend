"""Self-Healing RPA Adapter - 설정 기반 범용 RPA"""
import logging
from typing import Dict, Any, List, Optional
from playwright.async_api import Page, Locator

logger = logging.getLogger(__name__)


class SelfHealingAdapter:
    """
    Self-Healing RPA Adapter (하이브리드 구조)

    로그인: rpa_site_configs (공유)
    폼: campaigns (개별)

    여러 셀렉터 전략을 우선순위대로 시도하여 HTML 구조 변경에 자동 대응
    """

    def __init__(
        self,
        page: Page,
        login_config: Dict[str, Any],
        login_strategies: Optional[Dict[str, Any]] = None,
        form_config: Optional[Dict[str, Any]] = None,
        form_strategies: Optional[Dict[str, Any]] = None,
        field_mapping: Optional[Dict[str, str]] = None
    ):
        """
        Parameters:
        -----------
        page : Page
            Playwright Page 객체
        login_config : Dict[str, Any]
            로그인 셀렉터 설정 (rpa_site_configs.login_config)
        login_strategies : Optional[Dict[str, Any]]
            로그인 Self-Healing 전략 (rpa_site_configs.login_selector_strategies)
        form_config : Optional[Dict[str, Any]]
            폼 셀렉터 설정 (campaigns.rpa_form_config)
        form_strategies : Optional[Dict[str, Any]]
            폼 Self-Healing 전략 (campaigns.rpa_form_selector_strategies)
        field_mapping : Optional[Dict[str, str]]
            submission_data → 폼 셀렉터 매핑 (campaigns.rpa_field_mapping)
        """
        self.page = page
        self.login_config = login_config
        self.login_strategies = login_strategies or {}
        self.form_config = form_config or {}
        self.form_strategies = form_strategies or {}
        self.field_mapping = field_mapping or {}

    async def find_element(self, element_key: str, context: str = 'form') -> Locator:
        """
        여러 전략으로 요소 찾기 (Self-Healing)

        Parameters:
        -----------
        element_key : str
            찾을 요소 키 (예: 'username_input', 'submit_button')
        context : str
            컨텍스트 ('login' 또는 'form')

        Returns:
        --------
        Locator
            찾은 요소

        Raises:
        -------
        Exception
            모든 전략이 실패한 경우
        """
        # 1. context에 따라 전략과 설정 선택
        if context == 'login':
            strategies = self.login_strategies.get(element_key, [])
            config_source = self.login_config
        else:
            strategies = self.form_strategies.get(element_key, [])
            config_source = self.form_config

        # 2. 전략이 없으면 기본 셀렉터만 시도
        if not strategies:
            default_selector = config_source.get('selectors', {}).get(element_key)

            if default_selector:
                element = self.page.locator(default_selector)
                if await element.count() > 0:
                    logger.debug(f"Found '{element_key}' using default selector: {default_selector}")
                    return element.first
                raise Exception(f"Element '{element_key}' not found with default selector: {default_selector}")

            raise Exception(f"No selector found for element '{element_key}'")

        # 3. 전략을 우선순위대로 정렬
        strategies_sorted = sorted(strategies, key=lambda x: x.get('priority', 999))

        # 4. 우선순위대로 시도
        for strategy in strategies_sorted:
            selector = strategy.get('selector')
            priority = strategy.get('priority', 999)
            method = strategy.get('method', 'unknown')
            role = strategy.get('role')  # New: support role-based selection
            name = strategy.get('name')  # New: support name for getByRole

            if not selector and not role:
                continue

            try:
                # Method 1: Role-based selector (most reliable for buttons/inputs)
                if role and name:
                    logger.debug(f"Trying getByRole('{role}', name='{name}')")
                    element = self.page.get_by_role(role, name=name)

                # Method 2: Text-based selector with :has-text()
                elif selector and ':has-text(' in selector:
                    import re
                    match = re.search(r':has-text\(["\'](.+?)["\']\)', selector)
                    if match:
                        text = match.group(1)
                        tag = selector.split(':')[0] if ':' in selector else 'button'
                        element = self.page.locator(tag).filter(has_text=text)
                    else:
                        element = self.page.locator(selector)

                # Method 3: Standard CSS selector
                elif selector:
                    element = self.page.locator(selector)
                else:
                    continue

                if await element.count() > 0:
                    logger.info(
                        f"✅ Found '{element_key}' using strategy (priority={priority}, method={method}): {role or selector}"
                    )
                    return element.first
                else:
                    logger.debug(
                        f"⚠️  Strategy failed for '{element_key}' (priority={priority}): element not found"
                    )

            except Exception as e:
                logger.debug(
                    f"⚠️  Strategy failed for '{element_key}' (priority={priority}): {str(e)}"
                )
                continue

        # 5. 모든 전략 실패 - fallback to getByRole for common cases
        logger.warning(f"All strategies failed for '{element_key}', trying fallback methods...")

        # Fallback: try getByRole with element_key hints
        if 'button' in element_key.lower() or 'submit' in element_key.lower():
            # Try common button texts
            for text in ['등록하기', '등록', '제출', 'Submit', 'OK']:
                try:
                    element = self.page.get_by_role('button', name=text)
                    if await element.count() > 0:
                        logger.info(f"✅ Found '{element_key}' using fallback getByRole with text '{text}'")
                        return element.first
                except:
                    continue

        raise Exception(
            f"❌ All {len(strategies_sorted)} strategies failed for element '{element_key}'"
        )

    async def login(self, credentials: Dict[str, str]) -> bool:
        """
        설정 기반 로그인

        Parameters:
        -----------
        credentials : Dict[str, str]
            {"username": "...", "password": "..."}

        Returns:
        --------
        bool
            로그인 성공 여부
        """
        # Note: login_url should be handled by caller (rpa_core.py)
        # This method only handles filling login form

        logger.info("Filling login form")

        # 로그인 폼 입력
        try:
            username_input = await self.find_element('username_input', context='login')
            password_input = await self.find_element('password_input', context='login')

            await username_input.fill(credentials['username'])
            await password_input.fill(credentials['password'])

            logger.debug("Login credentials filled")

        except Exception as e:
            logger.error(f"Failed to fill login form: {e}")
            return False

        # 로그인 버튼 클릭
        try:
            submit_button = await self.find_element('submit_button', context='login')
            await submit_button.click()

            logger.debug("Login button clicked")

            # 페이지 전환 대기
            await self.page.wait_for_timeout(2000)

        except Exception as e:
            logger.error(f"Failed to click login button: {e}")
            return False

        # 로그인 에러 확인
        try:
            error_element = await self.find_element('error_message', context='login')

            if await error_element.count() > 0:
                error_text = await error_element.text_content()
                logger.error(f"Login failed: {error_text}")
                return False

        except Exception as e:
            # 에러 메시지 셀렉터를 찾을 수 없으면 성공으로 간주
            # (사이트마다 에러 메시지 없을 수 있음)
            logger.debug(f"No error message element found (this is OK): {e}")
            pass

        logger.info("✅ Login successful")
        return True

    async def navigate_to_form(self, form_url: Optional[str] = None) -> bool:
        """
        폼 페이지로 이동

        Parameters:
        -----------
        form_url : Optional[str]
            폼 페이지 URL

        Returns:
        --------
        bool
            이동 성공 여부
        """
        # form_url이 None이면 로그인 후 자동으로 폼이 나타남
        if not form_url:
            logger.info("No form_url provided - assuming form is on same page after login")
            return True

        logger.info(f"Navigating to form page: {form_url}")
        await self.page.goto(form_url, wait_until='networkidle', timeout=30000)

        return True

    async def fill_form(self, data: Dict[str, Any]) -> bool:
        """
        설정 기반 폼 작성

        Parameters:
        -----------
        data : Dict[str, Any]
            제출할 데이터
            예: {"user_name": "홍길동", "user_birth": "900101", "photo": "/path/to/image.jpg"}

        Returns:
        --------
        bool
            폼 작성 성공 여부
        """
        logger.info(f"Filling form with {len(data)} fields")

        filled_count = 0

        for data_key, data_value in data.items():
            # 1. field_mapping에서 셀렉터 키 찾기
            selector_key = self.field_mapping.get(data_key)

            if not selector_key:
                logger.warning(f"⚠️  No field mapping for data key '{data_key}' - skipping")
                continue

            # 2. 요소 찾아서 입력
            try:
                element = await self.find_element(selector_key, context='form')

                # 파일 업로드 필드인 경우 set_input_files 사용
                if selector_key == 'photo_upload' or 'file' in selector_key.lower():
                    logger.debug(f"Uploading file: {data_value}")
                    await element.set_input_files(str(data_value))
                else:
                    # 일반 텍스트 필드
                    await element.fill(str(data_value))

                logger.debug(f"✅ Filled '{data_key}' (→ {selector_key}) with '{data_value}'")
                filled_count += 1

            except Exception as e:
                logger.warning(f"⚠️  Failed to fill '{data_key}': {e}")
                continue

        logger.info(f"Form filling completed: {filled_count}/{len(data)} fields filled")

        return filled_count > 0

    async def submit_form(self) -> Dict[str, Any]:
        """
        폼 제출 및 결과 확인

        Returns:
        --------
        Dict[str, Any]
            {"success": bool, "message": str} 또는 {"success": bool, "error": str}
        """
        logger.info("Submitting form")

        try:
            submit_button = await self.find_element('submit_button', context='form')
            await submit_button.click()

            logger.debug("Submit button clicked")

            # 제출 후 응답 대기
            await self.page.wait_for_timeout(2000)

        except Exception as e:
            logger.error(f"Failed to click submit button: {e}")
            return {"success": False, "error": f"Submit failed: {str(e)}"}

        # 성공 메시지 확인
        try:
            success_element = await self.find_element('success_message', context='form')

            if await success_element.count() > 0:
                success_text = await success_element.text_content()
                logger.info(f"✅ Form submitted successfully: {success_text}")

                return {
                    "success": True,
                    "message": success_text.strip() if success_text else "Successfully submitted"
                }

        except Exception as e:
            # 성공 메시지 셀렉터 없으면 에러 확인으로 진행
            logger.debug(f"No success message element found: {e}")
            pass

        # 에러 메시지 확인
        try:
            error_element = await self.find_element('error_message', context='form')

            if await error_element.count() > 0:
                error_text = await error_element.text_content()
                logger.error(f"❌ Form submission failed: {error_text}")

                return {
                    "success": False,
                    "error": error_text.strip() if error_text else "Submission failed"
                }

        except Exception as e:
            # 에러 메시지도 없으면 확인 불가
            logger.debug(f"No error message element found: {e}")
            pass

        # 성공도 에러도 확인 못함
        logger.warning("⚠️  No confirmation message found after submission")
        return {
            "success": False,
            "error": "No confirmation received after submission"
        }
