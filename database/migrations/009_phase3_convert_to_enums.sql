-- Migration: Phase 3 - Convert TEXT columns to ENUM types
-- Description: TEXT 컬럼을 ENUM 타입으로 변환
-- Created: 2025-01-26
-- Prerequisites: 008_phase2_remove_rpa_columns.sql must be executed first

-- ===== Step 1: ENUM 타입 생성 =====

-- submission_type ENUM
CREATE TYPE submission_type_enum AS ENUM (
  'WEBVIEW_ASSISTED',
  'DIRECT_API',
  'MANUAL'
);

-- verification_type ENUM
CREATE TYPE verification_type_enum AS ENUM (
  'IMAGE',
  'QUIZ',
  'TEXT_REVIEW'
);

-- campaign_status ENUM
CREATE TYPE campaign_status_enum AS ENUM (
  'EXPECT',
  'ACTIVE',
  'EXPIRED'
);

-- campaign_category ENUM
CREATE TYPE campaign_category_enum AS ENUM (
  '재활용',
  '대중교통',
  '에너지절약',
  '제로웨이스트',
  '자연보호',
  '교육',
  '기타'
);

-- campaign_type ENUM
CREATE TYPE campaign_type_enum AS ENUM (
  'ONLINE',
  'OFFLINE'
);

-- mission_log_status ENUM
CREATE TYPE mission_log_status_enum AS ENUM (
  'IN_PROGRESS',
  'PENDING_VERIFICATION',
  'COMPLETED',
  'FAILED'
);

-- ===== Step 2: campaigns.submission_type 변환 =====
-- 기존 CHECK 제약조건 제거
ALTER TABLE campaigns
  DROP CONSTRAINT IF EXISTS campaigns_submission_type_check;

-- 타입 변환
ALTER TABLE campaigns
  ALTER COLUMN submission_type TYPE submission_type_enum
  USING submission_type::submission_type_enum;

-- 기본값 재설정
ALTER TABLE campaigns
  ALTER COLUMN submission_type SET DEFAULT 'MANUAL'::submission_type_enum;

-- ===== Step 3: mission_templates.verification_type 변환 =====
-- 기존 CHECK 제약조건 제거
ALTER TABLE mission_templates
  DROP CONSTRAINT IF EXISTS mission_templates_verification_type_check;

-- 타입 변환
ALTER TABLE mission_templates
  ALTER COLUMN verification_type TYPE verification_type_enum
  USING verification_type::verification_type_enum;

-- ===== Step 4: campaigns.status 변환 =====
-- 현재 status 컬럼이 이미 campaign_status 타입으로 되어있을 수 있으므로 확인 후 변환
DO $$
BEGIN
  -- status 컬럼이 TEXT 타입인 경우에만 변환
  IF (SELECT data_type FROM information_schema.columns
      WHERE table_name = 'campaigns' AND column_name = 'status') = 'text' THEN

    ALTER TABLE campaigns
      ALTER COLUMN status TYPE campaign_status_enum
      USING status::campaign_status_enum;

    ALTER TABLE campaigns
      ALTER COLUMN status SET DEFAULT 'ACTIVE'::campaign_status_enum;
  END IF;
END $$;

-- ===== Step 5: campaigns.category 변환 =====
-- category 컬럼이 NULL인 경우 기본값 설정
UPDATE campaigns
SET category = '기타'
WHERE category IS NULL;

-- CHECK 제약조건 제거 (있을 경우)
ALTER TABLE campaigns
  DROP CONSTRAINT IF EXISTS campaigns_category_check;

-- 타입 변환
ALTER TABLE campaigns
  ALTER COLUMN category TYPE campaign_category_enum
  USING category::campaign_category_enum;

-- ===== Step 6: campaigns.campaign_type 변환 =====
-- campaign_type이 NULL인 경우 기본값 설정
UPDATE campaigns
SET campaign_type = 'ONLINE'
WHERE campaign_type IS NULL;

-- CHECK 제약조건 제거 (있을 경우)
ALTER TABLE campaigns
  DROP CONSTRAINT IF EXISTS campaigns_campaign_type_check;

-- 타입 변환
ALTER TABLE campaigns
  ALTER COLUMN campaign_type TYPE campaign_type_enum
  USING campaign_type::campaign_type_enum;

-- 기본값 설정
ALTER TABLE campaigns
  ALTER COLUMN campaign_type SET DEFAULT 'ONLINE'::campaign_type_enum;

-- ===== Step 7: mission_logs.status 변환 =====
-- CHECK 제약조건 제거 (있을 경우)
ALTER TABLE mission_logs
  DROP CONSTRAINT IF EXISTS mission_logs_status_check;

-- 타입 변환
ALTER TABLE mission_logs
  ALTER COLUMN status TYPE mission_log_status_enum
  USING status::mission_log_status_enum;

-- 기본값 재설정
ALTER TABLE mission_logs
  ALTER COLUMN status SET DEFAULT 'IN_PROGRESS'::mission_log_status_enum;

-- ===== Step 8: 코멘트 업데이트 =====
COMMENT ON COLUMN campaigns.submission_type IS '캠페인 제출 방식 (ENUM)';
COMMENT ON COLUMN mission_templates.verification_type IS '검증 방식 (ENUM)';
COMMENT ON COLUMN campaigns.status IS '캠페인 상태 (ENUM)';
COMMENT ON COLUMN campaigns.category IS '캠페인 카테고리 (ENUM)';
COMMENT ON COLUMN campaigns.campaign_type IS '캠페인 유형 (ENUM)';
COMMENT ON COLUMN mission_logs.status IS '미션 상태 (ENUM)';
