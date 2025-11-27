-- Migration: Phase 1 - Data Migration for RPA Removal
-- Description: RPA 관련 데이터를 변환하여 새로운 구조로 마이그레이션
-- Created: 2025-01-26

-- ===== Step 1: campaigns.submission_type 데이터 변환 =====
-- RPA_FORM_SUBMIT → WEBVIEW_ASSISTED
UPDATE campaigns
SET submission_type = 'WEBVIEW_ASSISTED'
WHERE submission_type = 'RPA_FORM_SUBMIT';

-- MANUAL_GUIDE → MANUAL
UPDATE campaigns
SET submission_type = 'MANUAL'
WHERE submission_type = 'MANUAL_GUIDE';

-- ===== Step 2: mission_templates.verification_type 데이터 변환 =====
-- RPA_ACTION → TEXT_REVIEW
UPDATE mission_templates
SET verification_type = 'TEXT_REVIEW'
WHERE verification_type = 'RPA_ACTION';

-- ===== 변환 결과 확인 (선택적) =====
-- SELECT submission_type, COUNT(*) FROM campaigns GROUP BY submission_type;
-- SELECT verification_type, COUNT(*) FROM mission_templates GROUP BY verification_type;
