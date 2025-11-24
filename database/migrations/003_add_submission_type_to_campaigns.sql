-- Migration: Add submission_type to campaigns table
-- Description: 캠페인 제출 방식 컬럼 추가
-- Created: 2025-01-06

-- ===== campaigns 테이블에 submission_type 컬럼 추가 =====
ALTER TABLE campaigns
  ADD COLUMN IF NOT EXISTS submission_type TEXT
  CHECK (submission_type IN ('RPA_FORM_SUBMIT', 'DIRECT_API', 'MANUAL_GUIDE'))
  DEFAULT 'MANUAL_GUIDE';

-- ===== 코멘트 =====
COMMENT ON COLUMN campaigns.submission_type IS '캠페인 제출 방식: RPA_FORM_SUBMIT(RPA 자동 제출), DIRECT_API(API 연동), MANUAL_GUIDE(수동 안내)';
