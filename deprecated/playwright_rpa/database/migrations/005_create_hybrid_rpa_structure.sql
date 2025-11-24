-- Migration: Create hybrid RPA structure (login shared, form individual)
-- Description: 로그인 설정은 사이트별 공유, 폼 설정은 캠페인별 개별 관리
-- Created: 2025-01-10

-- ===== rpa_site_configs 테이블 생성 (로그인 설정만) =====
CREATE TABLE IF NOT EXISTS rpa_site_configs (
  id BIGSERIAL PRIMARY KEY,
  site_code TEXT UNIQUE NOT NULL,
  site_name TEXT NOT NULL,
  base_url TEXT NOT NULL,
  login_url TEXT NOT NULL,

  -- 로그인 설정 (JSONB) - 여러 Campaign이 공유
  -- 예시: {"selectors": {"username_input": "#username", "password_input": "#password", "submit_button": "button[type='submit']"}}
  login_config JSONB NOT NULL,

  -- Self-Healing 셀렉터 전략 (로그인용만)
  -- 예시: {"username_input": [{"selector": "#username", "priority": 1}, {"selector": "input[name='username']", "priority": 2}]}
  login_selector_strategies JSONB,

  -- 메타데이터
  is_active BOOLEAN DEFAULT true,
  last_verified_at TIMESTAMPTZ,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- ===== campaigns 테이블 확장 (폼 설정 추가) =====
-- RPA 사이트 설정 참조 (로그인용)
ALTER TABLE campaigns
ADD COLUMN IF NOT EXISTS rpa_site_config_id BIGINT REFERENCES rpa_site_configs(id) ON DELETE SET NULL;

-- 폼 제출 URL (Campaign별)
ALTER TABLE campaigns
ADD COLUMN IF NOT EXISTS rpa_form_url TEXT;

-- 폼 설정 (JSONB) - Campaign별 개별 관리
-- 예시: {"selectors": {"name_input": "input[name='name']", "birth_input": "#birth", "submit_button": "#submit-button"}}
ALTER TABLE campaigns
ADD COLUMN IF NOT EXISTS rpa_form_config JSONB;

-- 필드 매핑 (submission_data 키 → form selector 키)
-- 예시: {"user_name": "name_input", "user_birth": "birth_input"}
ALTER TABLE campaigns
ADD COLUMN IF NOT EXISTS rpa_field_mapping JSONB;

-- Self-Healing 셀렉터 전략 (폼용)
-- 예시: {"name_input": [{"selector": "input[name='name']", "priority": 1}, {"selector": "#name", "priority": 2}]}
ALTER TABLE campaigns
ADD COLUMN IF NOT EXISTS rpa_form_selector_strategies JSONB;

-- ===== 인덱스 생성 =====
-- 사이트 코드로 빠른 조회
CREATE INDEX IF NOT EXISTS idx_rpa_site_configs_site_code
  ON rpa_site_configs(site_code);

-- 활성화된 설정만 조회
CREATE INDEX IF NOT EXISTS idx_rpa_site_configs_active
  ON rpa_site_configs(is_active) WHERE is_active = true;

-- campaigns에서 RPA 설정 조회 최적화
CREATE INDEX IF NOT EXISTS idx_campaigns_rpa_site_config
  ON campaigns(rpa_site_config_id);

-- RPA 폼 설정이 있는 campaigns만 조회
CREATE INDEX IF NOT EXISTS idx_campaigns_rpa_form
  ON campaigns(rpa_site_config_id) WHERE rpa_form_config IS NOT NULL;

-- ===== 코멘트 =====
COMMENT ON TABLE rpa_site_configs IS 'RPA 사이트별 로그인 설정 (여러 Campaign이 공유)';
COMMENT ON COLUMN rpa_site_configs.site_code IS '사이트 고유 코드 (예: seoul_ecomileage)';
COMMENT ON COLUMN rpa_site_configs.site_name IS '사이트 표시 이름 (예: 서울시 에코마일리지)';
COMMENT ON COLUMN rpa_site_configs.base_url IS '사이트 기본 URL';
COMMENT ON COLUMN rpa_site_configs.login_url IS '로그인 페이지 URL';
COMMENT ON COLUMN rpa_site_configs.login_config IS '로그인 셀렉터 설정 (JSON) - 공통';
COMMENT ON COLUMN rpa_site_configs.login_selector_strategies IS 'Self-Healing용 로그인 셀렉터 전략 (JSON)';
COMMENT ON COLUMN rpa_site_configs.is_active IS '설정 활성화 여부';
COMMENT ON COLUMN rpa_site_configs.last_verified_at IS '마지막 검증 시간';

COMMENT ON COLUMN campaigns.rpa_site_config_id IS 'RPA 사이트 설정 ID (로그인 설정 참조)';
COMMENT ON COLUMN campaigns.rpa_form_url IS 'RPA 폼 제출 페이지 URL (Campaign별)';
COMMENT ON COLUMN campaigns.rpa_form_config IS 'RPA 폼 셀렉터 설정 (JSON) - Campaign별 개별';
COMMENT ON COLUMN campaigns.rpa_field_mapping IS 'submission_data 필드명 → 폼 셀렉터 매핑 (JSON)';
COMMENT ON COLUMN campaigns.rpa_form_selector_strategies IS 'Self-Healing용 폼 셀렉터 전략 (JSON)';
