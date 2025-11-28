-- Migration: Add LOCATION to verification_type_enum
-- Description: verification_type_enum에 LOCATION 값 추가 (위치 기반 인증)
-- Created: 2025-01-27
-- Prerequisites: 009_phase3_convert_to_enums.sql must be executed first

-- ===== Step 1: verification_type_enum에 LOCATION 값 추가 =====
ALTER TYPE verification_type_enum ADD VALUE 'LOCATION';

-- ===== Step 2: 코멘트 업데이트 =====
COMMENT ON COLUMN mission_templates.verification_type IS '검증 방식: IMAGE(사진), QUIZ(퀴즈), TEXT_REVIEW(소감문), LOCATION(위치 인증)';
