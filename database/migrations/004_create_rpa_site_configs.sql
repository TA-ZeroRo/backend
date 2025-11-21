-- Migration: Create rpa_site_configs table
-- Description: RPA 사이트별 설정 및 Self-Healing 셀렉터 전략 관리
-- Created: 2025-01-09

-- ===== rpa_site_configs 테이블 생성 =====
CREATE TABLE IF NOT EXISTS rpa_site_configs (
  id BIGSERIAL PRIMARY KEY,
  site_code TEXT UNIQUE NOT NULL,
  site_name TEXT NOT NULL,
  base_url TEXT NOT NULL,

  -- URL 설정
  login_url TEXT NOT NULL,
  form_url TEXT,  -- NULL이면 로그인 후 자동으로 폼이 나타남

  -- 로그인 설정 (JSONB)
  -- 예시: {"selectors": {"username_input": "#username", "password_input": "#password", ...}}
  login_config JSONB NOT NULL,

  -- 폼 설정 (JSONB)
  -- 예시: {"selectors": {"name_input": "input[name='name']", "submit_button": "#submit-button", ...}}
  form_config JSONB NOT NULL,

  -- Self-Healing 셀렉터 전략 (JSONB)
  -- 예시: {"username_input": [{"selector": "#username", "priority": 1}, {"selector": "input[name='userId']", "priority": 2}]}
  selector_strategies JSONB,

  -- 필드 매핑 (submission_data 키 → form selector 키)
  -- 예시: {"user_name": "name_input", "user_birth": "birth_input"}
  field_mapping JSONB,

  -- 메타데이터
  is_active BOOLEAN DEFAULT true,
  last_verified_at TIMESTAMPTZ,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- ===== mission_templates 테이블 확장 =====
-- RPA 사이트 설정 참조 추가
ALTER TABLE mission_templates
ADD COLUMN IF NOT EXISTS rpa_site_config_id BIGINT REFERENCES rpa_site_configs(id) ON DELETE SET NULL;

-- ===== 인덱스 생성 =====
-- 사이트 코드로 빠른 조회
CREATE INDEX IF NOT EXISTS idx_rpa_site_configs_site_code
  ON rpa_site_configs(site_code);

-- 활성화된 설정만 조회
CREATE INDEX IF NOT EXISTS idx_rpa_site_configs_active
  ON rpa_site_configs(is_active) WHERE is_active = true;

-- mission_templates에서 RPA 설정 조회 최적화
CREATE INDEX IF NOT EXISTS idx_mission_templates_rpa_config
  ON mission_templates(rpa_site_config_id);

-- ===== 코멘트 =====
COMMENT ON TABLE rpa_site_configs IS 'RPA 사이트별 설정 및 Self-Healing 전략';
COMMENT ON COLUMN rpa_site_configs.site_code IS '사이트 고유 코드 (예: seoul_ecomileage)';
COMMENT ON COLUMN rpa_site_configs.site_name IS '사이트 표시 이름';
COMMENT ON COLUMN rpa_site_configs.base_url IS '사이트 기본 URL';
COMMENT ON COLUMN rpa_site_configs.login_url IS '로그인 페이지 URL';
COMMENT ON COLUMN rpa_site_configs.form_url IS '폼 제출 페이지 URL (NULL이면 로그인 후 자동 표시)';
COMMENT ON COLUMN rpa_site_configs.login_config IS '로그인 셀렉터 설정 (JSON)';
COMMENT ON COLUMN rpa_site_configs.form_config IS '폼 셀렉터 설정 (JSON)';
COMMENT ON COLUMN rpa_site_configs.selector_strategies IS 'Self-Healing용 여러 셀렉터 전략 (JSON)';
COMMENT ON COLUMN rpa_site_configs.field_mapping IS 'submission_data 필드명 → 폼 셀렉터 매핑 (JSON)';
COMMENT ON COLUMN rpa_site_configs.is_active IS '설정 활성화 여부';
COMMENT ON COLUMN rpa_site_configs.last_verified_at IS '마지막 검증 시간';

COMMENT ON COLUMN mission_templates.rpa_site_config_id IS 'RPA 사이트 설정 ID (verification_type=RPA_ACTION일 때 필수)';
