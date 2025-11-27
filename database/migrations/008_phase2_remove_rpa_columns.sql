-- Migration: Phase 2 - Remove RPA Columns and Tables
-- Description: RPA 관련 컬럼 및 테이블 제거
-- Created: 2025-01-26
-- Prerequisites: 007_phase1_migrate_rpa_data.sql must be executed first

-- ===== Step 1: campaigns 테이블에서 RPA 관련 컬럼 제거 =====
ALTER TABLE campaigns
  DROP COLUMN IF EXISTS rpa_site_config_id,
  DROP COLUMN IF EXISTS rpa_form_url,
  DROP COLUMN IF EXISTS rpa_form_config,
  DROP COLUMN IF EXISTS rpa_field_mapping,
  DROP COLUMN IF EXISTS rpa_form_selector_strategies;

-- ===== Step 2: rpa_site_configs 테이블 제거 =====
-- 먼저 관련 인덱스 제거 (있을 경우)
DROP INDEX IF EXISTS idx_rpa_site_configs_site_code;
DROP INDEX IF EXISTS idx_rpa_site_configs_active;

-- 테이블 제거
DROP TABLE IF EXISTS rpa_site_configs CASCADE;

-- ===== Step 3: submission_type CHECK 제약조건 업데이트 =====
-- 기존 CHECK 제약조건 제거
ALTER TABLE campaigns
  DROP CONSTRAINT IF EXISTS campaigns_submission_type_check;

-- 새로운 CHECK 제약조건 추가 (RPA_FORM_SUBMIT, MANUAL_GUIDE 제외)
ALTER TABLE campaigns
  ADD CONSTRAINT campaigns_submission_type_check
  CHECK (submission_type IN ('WEBVIEW_ASSISTED', 'DIRECT_API', 'MANUAL'));

-- ===== Step 4: verification_type CHECK 제약조건 업데이트 =====
-- 기존 CHECK 제약조건 제거
ALTER TABLE mission_templates
  DROP CONSTRAINT IF EXISTS mission_templates_verification_type_check;

-- 새로운 CHECK 제약조건 추가 (RPA_ACTION 제외)
ALTER TABLE mission_templates
  ADD CONSTRAINT mission_templates_verification_type_check
  CHECK (verification_type IN ('IMAGE', 'QUIZ', 'TEXT_REVIEW'));

-- ===== Step 5: 코멘트 업데이트 =====
COMMENT ON COLUMN campaigns.submission_type IS '캠페인 제출 방식: WEBVIEW_ASSISTED(웹뷰 반자동), DIRECT_API(API 연동), MANUAL(수동 안내)';
COMMENT ON COLUMN mission_templates.verification_type IS '검증 방식: IMAGE(사진), QUIZ(퀴즈), TEXT_REVIEW(소감문)';
