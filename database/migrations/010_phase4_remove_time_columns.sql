-- Migration: Phase 4 - Remove time columns from offline_campaign_locations
-- Description: offline_campaign_locations 테이블에서 시간 관련 컬럼 제거
-- Created: 2025-01-26

-- ===== Step 1: offline_campaign_locations 테이블에서 시간 컬럼 제거 =====
ALTER TABLE offline_campaign_locations
  DROP COLUMN IF EXISTS daily_start_time,
  DROP COLUMN IF EXISTS daily_end_time;

-- ===== 변경 결과 확인 (선택적) =====
-- SELECT column_name, data_type
-- FROM information_schema.columns
-- WHERE table_name = 'offline_campaign_locations'
-- ORDER BY ordinal_position;
