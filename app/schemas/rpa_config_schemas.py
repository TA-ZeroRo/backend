"""RPA Config 관련 Pydantic 스키마"""
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime


class SelectorStrategy(BaseModel):
    """셀렉터 전략"""
    selector: str = Field(..., description="CSS 셀렉터")
    priority: int = Field(..., description="우선순위 (낮을수록 먼저 시도)")
    method: Optional[str] = Field(None, description="식별 방법 (id, class, name, xpath 등)")


class LoginConfigSelectors(BaseModel):
    """로그인 셀렉터 설정"""
    username_input: str
    password_input: str
    submit_button: str
    error_message: Optional[str] = None


class LoginConfig(BaseModel):
    """로그인 설정"""
    selectors: LoginConfigSelectors


class FormConfigSelectors(BaseModel):
    """폼 셀렉터 설정"""
    submit_button: str
    success_message: Optional[str] = None
    error_message: Optional[str] = None


class FormConfig(BaseModel):
    """폼 설정"""
    selectors: Dict[str, str] = Field(..., description="폼 필드 셀렉터 맵")


class RPAConfigBase(BaseModel):
    """RPA Config 기본 스키마 (로그인 설정만 - 하이브리드 구조)"""
    site_code: str = Field(..., min_length=1, max_length=100, description="사이트 고유 코드")
    site_name: str = Field(..., min_length=1, max_length=200, description="사이트 표시 이름")
    base_url: str = Field(..., description="사이트 기본 URL")
    login_url: str = Field(..., description="로그인 페이지 URL")
    login_config: Dict[str, Any] = Field(..., description="로그인 셀렉터 설정 (공통)")
    login_selector_strategies: Optional[Dict[str, List[Dict[str, Any]]]] = Field(
        None,
        description="Self-Healing 로그인 셀렉터 전략"
    )
    is_active: bool = Field(True, description="설정 활성화 여부")


class RPAConfigCreate(RPAConfigBase):
    """RPA Config 생성 스키마"""
    pass


class RPAConfigUpdate(BaseModel):
    """RPA Config 업데이트 스키마 (로그인 설정만)"""
    site_name: Optional[str] = Field(None, min_length=1, max_length=200)
    base_url: Optional[str] = None
    login_url: Optional[str] = None
    login_config: Optional[Dict[str, Any]] = None
    login_selector_strategies: Optional[Dict[str, List[Dict[str, Any]]]] = None
    is_active: Optional[bool] = None


class RPAConfigResponse(RPAConfigBase):
    """RPA Config 응답 스키마"""
    id: int
    last_verified_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class AddSelectorStrategyRequest(BaseModel):
    """셀렉터 전략 추가 요청"""
    site_code: str = Field(..., description="사이트 코드")
    element_key: str = Field(..., description="요소 키 (예: username_input)")
    selector: str = Field(..., description="CSS 셀렉터")
    priority: int = Field(..., description="우선순위 (낮을수록 먼저 시도)")
    method: str = Field("unknown", description="식별 방법")
