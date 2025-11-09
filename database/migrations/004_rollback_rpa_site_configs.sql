-- Rollback: Remove rpa_site_configs table and mission_templates column
-- Description: 기존 RPA 구조 롤백 (하이브리드 구조로 재설계 위해)
-- Created: 2025-01-10

-- ===== 인덱스 삭제 =====
DROP INDEX IF EXISTS idx_mission_templates_rpa_config;
DROP INDEX IF EXISTS idx_rpa_site_configs_active;
DROP INDEX IF EXISTS idx_rpa_site_configs_site_code;

-- ===== mission_templates 테이블 복구 =====
ALTER TABLE mission_templates
DROP COLUMN IF EXISTS rpa_site_config_id;

-- ===== rpa_site_configs 테이블 삭제 =====
DROP TABLE IF EXISTS rpa_site_configs CASCADE;
