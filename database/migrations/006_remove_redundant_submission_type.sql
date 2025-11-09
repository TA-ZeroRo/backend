-- Migration: Remove redundant submission_type column
-- Description: submission_type은 rpa_site_config_id로 판단 가능하므로 제거
-- Created: 2025-01-10

-- ===== submission_type 컬럼 제거 =====
-- rpa_site_config_id가 NOT NULL이면 RPA 사용, NULL이면 MANUAL_GUIDE

ALTER TABLE campaigns
DROP COLUMN IF EXISTS submission_type;

-- ===== View 생성 (하위 호환성) =====
-- 기존 코드가 submission_type을 참조하는 경우를 위해 View 제공

CREATE OR REPLACE VIEW campaigns_with_submission_type AS
SELECT
  c.*,
  CASE
    WHEN c.rpa_site_config_id IS NOT NULL THEN 'RPA_FORM_SUBMIT'
    ELSE 'MANUAL_GUIDE'
  END as submission_type
FROM campaigns c;

-- ===== 코멘트 =====
COMMENT ON VIEW campaigns_with_submission_type IS '하위 호환성을 위한 View: submission_type을 동적으로 계산';

-- ===== 검증 쿼리 =====
-- RPA 설정이 있는 Campaign들
SELECT
  id,
  title,
  rpa_site_config_id,
  CASE
    WHEN rpa_site_config_id IS NOT NULL THEN 'RPA_FORM_SUBMIT'
    ELSE 'MANUAL_GUIDE'
  END as computed_submission_type
FROM campaigns
WHERE rpa_site_config_id IS NOT NULL;
