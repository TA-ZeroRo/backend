"""WebView RPA Endpoints - JavaScript Channel 기반 RPA API"""
import logging
from fastapi import APIRouter, HTTPException, Depends

from app.schemas.rpa_webview_schemas import (
    WebViewScriptRequest,
    WebViewScriptResponse,
    LoginDetectorConfig,
    RPAConfigResponse,
    ReportFailureRequest
)
from app.services.rpa_webview_service import RPAWebViewService

logger = logging.getLogger(__name__)

router = APIRouter()


def get_rpa_webview_service() -> RPAWebViewService:
    """RPAWebViewService 의존성 주입"""
    return RPAWebViewService()


@router.post("/generate-script", response_model=WebViewScriptResponse)
async def generate_webview_script(
    request: WebViewScriptRequest,
    service: RPAWebViewService = Depends(get_rpa_webview_service)
):
    """
    WebView 폼 자동 입력용 JavaScript 생성

    ## 설명
    Campaign과 MissionTemplate 데이터를 기반으로 WebView에서 실행할
    JavaScript 코드를 생성합니다. 생성된 JavaScript는 폼의 제목과 내용을
    자동으로 입력하고, 사진 업로드 필드와 제출 버튼을 하이라이트합니다.

    ## Parameters
    - **campaign_id**: 캠페인 ID
    - **mission_template_id**: 미션 템플릿 ID
    - **user_id**: 사용자 ID
    - **proof_image_url**: 인증 이미지 URL (선택)

    ## Returns
    - **success**: 생성 성공 여부
    - **javascript_code**: WebView에서 실행할 JavaScript 코드
    - **field_mapping**: 필드명과 셀렉터 매핑
    - **submit_selector**: 제출 버튼 셀렉터
    - **error**: 에러 메시지 (실패 시)

    ## Example Request
    ```json
    {
        "campaign_id": 1,
        "mission_template_id": 5,
        "user_id": "550e8400-e29b-41d4-a716-446655440000"
    }
    ```

    ## Example Response
    ```json
    {
        "success": true,
        "javascript_code": "(function() { ... })();",
        "field_mapping": {
            "title_field": "input[placeholder='제목을 입력하세요']",
            "content_field": "textarea[placeholder='내용을 입력하세요']"
        },
        "submit_selector": "button:has-text('등록하기')"
    }
    ```
    """
    try:
        logger.info(f"Generating JavaScript for campaign {request.campaign_id}, "
                   f"mission template {request.mission_template_id}")

        response = await service.generate_javascript_code(
            campaign_id=request.campaign_id,
            mission_template_id=request.mission_template_id,
            user_id=request.user_id,
            proof_image_url=request.proof_image_url
        )

        if not response.success:
            raise HTTPException(status_code=400, detail=response.error)

        return response

    except ValueError as e:
        logger.error(f"Validation error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/login-detector/{campaign_id}", response_model=LoginDetectorConfig)
async def get_login_detector_config(
    campaign_id: int,
    service: RPAWebViewService = Depends(get_rpa_webview_service)
):
    """
    로그인 감지 설정 조회

    ## 설명
    WebView에서 사용자의 로그인 성공을 감지하기 위한 설정을 반환합니다.
    URL 변화, DOM 요소 존재 여부 등의 조건을 제공합니다.

    ## Parameters
    - **campaign_id**: 캠페인 ID

    ## Returns
    - **login_url**: 로그인 페이지 URL
    - **form_url**: 폼 제출 페이지 URL
    - **login_success_indicators**: 로그인 성공 감지 조건 리스트
    - **modal_trigger**: 모달 트리거 셀렉터 (선택)

    ## Example Response
    ```json
    {
        "login_url": "https://event.seoul.go.kr/zeroseoul/login",
        "form_url": "https://event.seoul.go.kr/zeroseoul/",
        "login_success_indicators": [
            {"type": "url_contains", "value": "/zeroseoul/"},
            {"type": "dom_exists", "selector": ".user-profile"}
        ],
        "modal_trigger": "a[href='/zeroseoul/']:has-text('미션인증하기')"
    }
    ```
    """
    try:
        logger.info(f"Getting login detector config for campaign {campaign_id}")
        return await service.get_login_detector_config(campaign_id)

    except ValueError as e:
        logger.error(f"Campaign not found: {e}")
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/campaigns/{campaign_id}/config", response_model=RPAConfigResponse)
async def get_rpa_config(
    campaign_id: int,
    service: RPAWebViewService = Depends(get_rpa_webview_service)
):
    """
    RPA 설정 조회 (사이트 + 폼 설정)

    ## 설명
    Campaign의 RPA 관련 설정을 조회합니다.
    사이트 정보와 폼 필드 매핑 정보를 포함합니다.

    ## Parameters
    - **campaign_id**: 캠페인 ID

    ## Returns
    - **campaign_id**: 캠페인 ID
    - **site_config**: 사이트 설정 (로그인 URL 등)
    - **form_config**: 폼 설정 (필드 매핑 등)

    ## Example Response
    ```json
    {
        "campaign_id": 1,
        "site_config": {
            "site_code": "zeroseoul",
            "site_name": "제로서울",
            "login_url": "https://event.seoul.go.kr/zeroseoul/login"
        },
        "form_config": {
            "form_url": "https://event.seoul.go.kr/zeroseoul/",
            "field_mapping": {
                "title_field": "input[placeholder='제목을 입력하세요']",
                "content_field": "textarea[placeholder='내용을 입력하세요']"
            }
        }
    }
    ```
    """
    try:
        logger.info(f"Getting RPA config for campaign {campaign_id}")
        return await service.get_rpa_config(campaign_id)

    except ValueError as e:
        logger.error(f"Campaign not found: {e}")
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.post("/report-failure", status_code=200)
async def report_selector_failure(request: ReportFailureRequest):
    """
    셀렉터 실패 보고 (Analytics용)

    ## 설명
    WebView에서 특정 셀렉터가 요소를 찾지 못했을 때 보고합니다.
    향후 Self-Healing 전략 개선에 사용됩니다.

    ## Parameters
    - **campaign_id**: 캠페인 ID
    - **element_key**: 실패한 요소 키 (예: 'title_field')
    - **failed_strategies**: 실패한 셀렉터 전략 리스트
    - **user_agent**: 사용자 에이전트 정보 (선택)

    ## Example Request
    ```json
    {
        "campaign_id": 1,
        "element_key": "title_field",
        "failed_strategies": [
            {"selector": "input[placeholder='제목']", "priority": 10},
            {"selector": "input[name='title']", "priority": 20}
        ],
        "user_agent": "Mozilla/5.0 (Linux; Android 12) AppleWebKit/537.36"
    }
    ```

    ## Returns
    ```json
    {
        "success": true,
        "message": "Failure report recorded"
    }
    ```

    ## Note
    현재는 로깅만 수행하며, 향후 DB 저장 기능이 추가될 예정입니다.
    """
    try:
        logger.warning(
            f"Selector failure reported - Campaign: {request.campaign_id}, "
            f"Element: {request.element_key}, "
            f"Strategies: {request.failed_strategies}, "
            f"User Agent: {request.user_agent}"
        )

        # TODO: DB에 실패 로그 저장 (향후 Self-Healing 개선용)
        # await rpa_failure_log_repo.create_log(...)

        return {
            "success": True,
            "message": "Failure report recorded"
        }

    except Exception as e:
        logger.error(f"Error recording failure report: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
