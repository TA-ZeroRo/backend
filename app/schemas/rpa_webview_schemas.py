"""WebView RPA Schemas - JavaScript Channel 기반 RPA 스키마"""
from pydantic import BaseModel, Field
from typing import Dict, Any, Optional, List


class WebViewScriptRequest(BaseModel):
    """WebView JavaScript 생성 요청 스키마"""
    campaign_id: int = Field(..., description="캠페인 ID")
    mission_template_id: int = Field(..., description="미션 템플릿 ID")
    user_id: str = Field(..., description="사용자 ID")
    proof_image_url: Optional[str] = Field(None, description="인증 이미지 URL (선택)")

    class Config:
        json_schema_extra = {
            "example": {
                "campaign_id": 1,
                "mission_template_id": 5,
                "user_id": "550e8400-e29b-41d4-a716-446655440000",
                "proof_image_url": "https://storage.example.com/images/mission_photo.jpg"
            }
        }


class WebViewScriptResponse(BaseModel):
    """WebView JavaScript 생성 응답 스키마"""
    success: bool = Field(..., description="생성 성공 여부")
    javascript_code: str = Field(..., description="WebView에서 실행할 JavaScript 코드")
    field_mapping: Dict[str, str] = Field(..., description="필드명과 셀렉터 매핑")
    submit_selector: Optional[str] = Field(None, description="제출 버튼 셀렉터")
    error: Optional[str] = Field(None, description="에러 메시지 (실패 시)")

    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "javascript_code": "(function() { ... })();",
                "field_mapping": {
                    "title_field": "input[placeholder='제목을 입력하세요']",
                    "content_field": "textarea[placeholder='내용을 입력하세요']"
                },
                "submit_selector": "button:has-text('등록하기')",
                "error": None
            }
        }


class LoginDetectorConfig(BaseModel):
    """로그인 감지 설정 스키마"""
    login_url: str = Field(..., description="로그인 페이지 URL")
    form_url: str = Field(..., description="폼 제출 페이지 URL")
    login_success_indicators: List[Dict[str, str]] = Field(..., description="로그인 성공 감지 조건 리스트")
    modal_trigger: Optional[str] = Field(None, description="모달 트리거 셀렉터")

    class Config:
        json_schema_extra = {
            "example": {
                "login_url": "https://event.seoul.go.kr/zeroseoul/login",
                "form_url": "https://event.seoul.go.kr/zeroseoul/",
                "login_success_indicators": [
                    {"type": "url_contains", "value": "/zeroseoul/"},
                    {"type": "dom_exists", "selector": ".user-profile"}
                ],
                "modal_trigger": "a[href='/zeroseoul/']:has-text('미션인증하기')"
            }
        }


class RPAConfigResponse(BaseModel):
    """RPA 설정 조회 응답 스키마"""
    campaign_id: int = Field(..., description="캠페인 ID")
    site_config: Dict[str, Any] = Field(..., description="사이트 설정 (로그인)")
    form_config: Dict[str, Any] = Field(..., description="폼 설정 (필드 매핑)")

    class Config:
        json_schema_extra = {
            "example": {
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
        }


class ReportFailureRequest(BaseModel):
    """셀렉터 실패 보고 요청 스키마"""
    campaign_id: int = Field(..., description="캠페인 ID")
    element_key: str = Field(..., description="실패한 요소 키 (예: 'title_field')")
    failed_strategies: List[Dict[str, Any]] = Field(..., description="실패한 셀렉터 전략 리스트")
    user_agent: Optional[str] = Field(None, description="사용자 에이전트 정보")

    class Config:
        json_schema_extra = {
            "example": {
                "campaign_id": 1,
                "element_key": "title_field",
                "failed_strategies": [
                    {"selector": "input[placeholder='제목']", "priority": 10},
                    {"selector": "input[name='title']", "priority": 20}
                ],
                "user_agent": "Mozilla/5.0 (Linux; Android 12) AppleWebKit/537.36"
            }
        }
