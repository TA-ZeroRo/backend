"""WebView RPA Service - JavaScript 생성 및 WebView RPA 비즈니스 로직"""
import logging
import json
from typing import Dict, Any, Optional

from app.repository.campaign_repository import CampaignRepository
from app.repository.mission_template_repository import MissionTemplateRepository
from app.schemas.rpa_webview_schemas import (
    WebViewScriptResponse,
    LoginDetectorConfig,
    RPAConfigResponse
)

logger = logging.getLogger(__name__)


class RPAWebViewService:
    """
    WebView 기반 RPA 서비스

    JavaScript 코드 생성, 로그인 감지 설정 조회 등을 처리
    """

    def __init__(self):
        self.campaign_repo = CampaignRepository()
        self.mission_template_repo = MissionTemplateRepository()

    async def generate_javascript_code(
        self,
        campaign_id: int,
        mission_template_id: int,
        user_id: str,
        proof_image_url: Optional[str] = None
    ) -> WebViewScriptResponse:
        """
        미션 데이터 기반 JavaScript 코드 생성

        Parameters:
        -----------
        campaign_id : int
            캠페인 ID
        mission_template_id : int
            미션 템플릿 ID
        user_id : str
            사용자 ID
        proof_image_url : Optional[str]
            인증 이미지 URL

        Returns:
        --------
        WebViewScriptResponse
            생성된 JavaScript 코드 및 메타데이터
        """
        try:
            # 1. Campaign 데이터 조회
            campaign = await self.campaign_repo.get_campaign_by_id(campaign_id)
            if not campaign:
                return WebViewScriptResponse(
                    success=False,
                    javascript_code="",
                    field_mapping={},
                    error=f"Campaign not found: {campaign_id}"
                )

            # 2. MissionTemplate 데이터 조회
            mission_template = await self.mission_template_repo.get_template_by_id(mission_template_id)
            if not mission_template:
                return WebViewScriptResponse(
                    success=False,
                    javascript_code="",
                    field_mapping={},
                    error=f"Mission template not found: {mission_template_id}"
                )

            # 3. RPA 설정 추출 (DB 구조 완전 활용)
            rpa_form_config = campaign.get('rpa_form_config', {})
            rpa_field_mapping = campaign.get('rpa_field_mapping', {})
            rpa_selector_strategies = campaign.get('rpa_form_selector_strategies', {})

            if not rpa_form_config:
                logger.warning(f"No rpa_form_config found for campaign {campaign_id}")
                return WebViewScriptResponse(
                    success=False,
                    javascript_code="",
                    field_mapping={},
                    error="Campaign does not have RPA form configuration"
                )

            # 4. 입력 데이터 결정 (우선순위: rpa_field_mapping > mission_template)
            # rpa_field_mapping에 실제 입력 데이터가 있으면 사용, 없으면 템플릿 사용
            title = rpa_field_mapping.get('제목', mission_template.get('title', ''))
            description = rpa_field_mapping.get('컨텐츠', mission_template.get('description', ''))

            logger.info(f"Using data source - title from: {'rpa_field_mapping' if '제목' in rpa_field_mapping else 'mission_template'}")

            # 5. JavaScript 코드 생성 (Self-Healing 전략 포함)
            js_code = self._build_javascript(
                form_config=rpa_form_config,
                selector_strategies=rpa_selector_strategies,
                title=title,
                description=description,
                proof_image_url=proof_image_url
            )

            logger.info(f"Generated JavaScript for campaign {campaign_id}, mission template {mission_template_id}")

            return WebViewScriptResponse(
                success=True,
                javascript_code=js_code,
                field_mapping=rpa_form_config,  # 셀렉터 정보 반환
                submit_selector=rpa_form_config.get('제출 버튼'),
                error=None
            )

        except Exception as e:
            logger.error(f"Error generating JavaScript: {e}", exc_info=True)
            return WebViewScriptResponse(
                success=False,
                javascript_code="",
                field_mapping={},
                error=str(e)
            )

    def _build_javascript(
        self,
        form_config: Dict[str, str],
        selector_strategies: Dict[str, list],
        title: str,
        description: str,
        proof_image_url: Optional[str] = None
    ) -> str:
        """
        JavaScript 코드 생성 (DB 구조 완전 활용 + Self-Healing 전략)

        Parameters:
        -----------
        form_config : Dict[str, str]
            DB의 rpa_form_config - 한글 필드명과 기본 셀렉터 매핑
            예: {"제목 입력란": "input[name='title']", "컨텐츠 작성란": "textarea#content"}
        selector_strategies : Dict[str, list]
            DB의 rpa_form_selector_strategies - Self-Healing용 예비 셀렉터
            예: {"제목 입력란": [{"selector": "input[placeholder*='제목']", "priority": 20}]}
        title : str
            미션 제목 (rpa_field_mapping['제목'] 또는 mission_template.title)
        description : str
            미션 설명 (rpa_field_mapping['컨텐츠'] 또는 mission_template.description)
        proof_image_url : Optional[str]
            인증 이미지 URL (현재 미사용)

        Returns:
        --------
        str
            생성된 JavaScript 코드 (Self-Healing 로직 포함)
        """
        js_lines = [
            "(function() {",
            "  try {",
            "    console.log('[RPA WebView] Starting form auto-fill...');",
            "",
            "    // Self-Healing Helper: 여러 셀렉터를 우선순위대로 시도",
            "    function findElementWithFallback(primarySelector, fallbackStrategies) {",
            "      let element = document.querySelector(primarySelector);",
            "      if (element) {",
            "        console.log('[RPA WebView] Primary selector worked:', primarySelector);",
            "        return element;",
            "      }",
            "      // 예비 셀렉터 시도 (우선순위 낮은 순서대로)",
            "      if (fallbackStrategies && fallbackStrategies.length > 0) {",
            "        const sorted = fallbackStrategies.sort((a, b) => a.priority - b.priority);",
            "        for (const strategy of sorted) {",
            "          element = document.querySelector(strategy.selector);",
            "          if (element) {",
            "            console.log('[RPA WebView] Fallback selector worked:', strategy.selector);",
            "            return element;",
            "          }",
            "        }",
            "      }",
            "      console.warn('[RPA WebView] No selector worked for:', primarySelector);",
            "      return null;",
            "    }",
            ""
        ]

        # 제목 입력 (DB의 "제목 입력란" 사용)
        title_selector = form_config.get('제목 입력란') or form_config.get('제목')
        if title_selector:
            title_fallbacks = selector_strategies.get('제목 입력란', [])
            escaped_title = title.replace("'", "\\'").replace('"', '\\"').replace('\n', '\\n')

            fallback_json = json.dumps(title_fallbacks) if title_fallbacks else "[]"

            js_lines.extend([
                f"    // 제목 입력",
                f"    const titleInput = findElementWithFallback('{title_selector}', {fallback_json});",
                f"    if (titleInput) {{",
                f"      titleInput.value = `{escaped_title}`;",
                f"      titleInput.dispatchEvent(new Event('input', {{bubbles: true}}));",
                f"      titleInput.dispatchEvent(new Event('change', {{bubbles: true}}));",
                f"      console.log('[RPA WebView] Title filled successfully');",
                f"    }} else {{",
                f"      console.warn('[RPA WebView] Title input not found');",
                f"    }}",
                ""
            ])

        # 내용 입력 (DB의 "컨텐츠 작성란" 사용)
        content_selector = form_config.get('컨텐츠 작성란') or form_config.get('컨텐츠') or form_config.get('내용')
        if content_selector:
            content_fallbacks = selector_strategies.get('컨텐츠 작성란', [])
            escaped_description = description.replace("'", "\\'").replace('"', '\\"').replace('\n', '\\n')

            fallback_json = json.dumps(content_fallbacks) if content_fallbacks else "[]"

            js_lines.extend([
                f"    // 내용 입력",
                f"    const contentInput = findElementWithFallback('{content_selector}', {fallback_json});",
                f"    if (contentInput) {{",
                f"      contentInput.value = `{escaped_description}`;",
                f"      contentInput.dispatchEvent(new Event('input', {{bubbles: true}}));",
                f"      contentInput.dispatchEvent(new Event('change', {{bubbles: true}}));",
                f"      console.log('[RPA WebView] Content filled successfully');",
                f"    }} else {{",
                f"      console.warn('[RPA WebView] Content input not found');",
                f"    }}",
                ""
            ])

        # 사진 필드 하이라이트 (DB의 "사진 업로드" 사용)
        photo_selector = form_config.get('사진 업로드') or form_config.get('사진') or form_config.get('이미지')
        if photo_selector:
            photo_fallbacks = selector_strategies.get('사진 업로드', [])
            fallback_json = json.dumps(photo_fallbacks) if photo_fallbacks else "[]"

            js_lines.extend([
                f"    // 사진 필드 하이라이트 (수동 업로드 필요)",
                f"    const photoInput = findElementWithFallback('{photo_selector}', {fallback_json});",
                f"    if (photoInput) {{",
                f"      photoInput.scrollIntoView({{behavior: 'smooth', block: 'center'}});",
                f"      photoInput.style.border = '3px solid #4CAF50';",
                f"      photoInput.style.boxShadow = '0 0 10px #4CAF50';",
                f"      console.log('[RPA WebView] Photo field highlighted');",
                f"    }}",
                ""
            ])

        # 제출 버튼 하이라이트 (DB의 "제출 버튼" 사용)
        submit_selector = form_config.get('제출 버튼') or form_config.get('등록 버튼')
        if submit_selector:
            submit_fallbacks = selector_strategies.get('제출 버튼', [])
            fallback_json = json.dumps(submit_fallbacks) if submit_fallbacks else "[]"

            js_lines.extend([
                f"    // 제출 버튼 하이라이트",
                f"    const submitButton = findElementWithFallback('{submit_selector}', {fallback_json});",
                f"    if (submitButton) {{",
                f"      submitButton.scrollIntoView({{behavior: 'smooth', block: 'center'}});",
                f"      submitButton.style.border = '3px solid #FF9800';",
                f"      submitButton.style.boxShadow = '0 0 10px #FF9800';",
                f"      console.log('[RPA WebView] Submit button highlighted');",
                f"    }}",
                ""
            ])

        # Flutter로 완료 메시지 전송
        js_lines.extend([
            "    // Flutter로 완료 알림",
            "    if (window.FlutterChannel) {",
            "      window.FlutterChannel.postMessage(JSON.stringify({",
            "        status: 'filled',",
            "        message: '폼 입력 완료. 사진을 업로드한 후 제출하세요.'",
            "      }));",
            "    }",
            "",
            "    console.log('[RPA WebView] Auto-fill completed successfully');",
            "    return 'success';",
            "",
            "  } catch (error) {",
            "    console.error('[RPA WebView] Error:', error);",
            "    if (window.FlutterChannel) {",
            "      window.FlutterChannel.postMessage(JSON.stringify({",
            "        status: 'error',",
            "        message: 'JavaScript 실행 중 오류: ' + error.toString()",
            "      }));",
            "    }",
            "    return 'error: ' + error.toString();",
            "  }",
            "})();"
        ])

        return "\n".join(js_lines)

    async def get_login_detector_config(self, campaign_id: int) -> LoginDetectorConfig:
        """
        로그인 감지 설정 조회

        Parameters:
        -----------
        campaign_id : int
            캠페인 ID

        Returns:
        --------
        LoginDetectorConfig
            로그인 감지 설정
        """
        try:
            campaign = await self.campaign_repo.get_campaign_by_id(campaign_id)
            if not campaign:
                raise ValueError(f"Campaign not found: {campaign_id}")

            # WebView 설정 추출 (없으면 기본값)
            webview_config = campaign.get('webview_config', {})

            login_url = webview_config.get('login_url') or campaign.get('rpa_form_url', '')
            form_url = campaign.get('rpa_form_url', '')

            # 기본 로그인 감지 조건
            login_success_indicators = webview_config.get('login_success_indicators', [
                {"type": "url_not_contains", "value": "/login"},
                {"type": "url_contains", "value": form_url.split('//')[-1].split('/')[1] if '//' in form_url else ""}
            ])

            modal_trigger = webview_config.get('modal_trigger')

            return LoginDetectorConfig(
                login_url=login_url,
                form_url=form_url,
                login_success_indicators=login_success_indicators,
                modal_trigger=modal_trigger
            )

        except Exception as e:
            logger.error(f"Error getting login detector config: {e}", exc_info=True)
            raise

    async def get_rpa_config(self, campaign_id: int) -> RPAConfigResponse:
        """
        RPA 설정 조회 (사이트 + 폼 설정)

        Parameters:
        -----------
        campaign_id : int
            캠페인 ID

        Returns:
        --------
        RPAConfigResponse
            RPA 설정
        """
        try:
            campaign = await self.campaign_repo.get_campaign_by_id(campaign_id)
            if not campaign:
                raise ValueError(f"Campaign not found: {campaign_id}")

            site_config = {
                "site_code": campaign.get('site_code', 'unknown'),
                "site_name": campaign.get('title', ''),
                "login_url": campaign.get('rpa_form_url', '')
            }

            form_config = {
                "form_url": campaign.get('rpa_form_url', ''),
                "field_mapping": campaign.get('rpa_field_mapping', {}),
                "form_selector_strategies": campaign.get('rpa_form_selector_strategies', {})
            }

            return RPAConfigResponse(
                campaign_id=campaign_id,
                site_config=site_config,
                form_config=form_config
            )

        except Exception as e:
            logger.error(f"Error getting RPA config: {e}", exc_info=True)
            raise
