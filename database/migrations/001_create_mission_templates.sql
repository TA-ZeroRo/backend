-- Migration: Create mission_templates table
-- Description: 캠페인별 미션 템플릿 정의
-- Created: 2025-01-06

-- ===== mission_templates 테이블 생성 =====
CREATE TABLE IF NOT EXISTS mission_templates (
  id BIGSERIAL PRIMARY KEY,
  campaign_id INTEGER NOT NULL REFERENCES campaigns(id) ON DELETE CASCADE,
  title TEXT NOT NULL,
  description TEXT,
  "order" INTEGER NOT NULL DEFAULT 0,
  verification_type TEXT NOT NULL CHECK (
    verification_type IN ('IMAGE', 'QUIZ', 'TEXT_REVIEW', 'RPA_ACTION')
  ),
  reward_points INTEGER NOT NULL DEFAULT 0 CHECK (reward_points >= 0),
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- ===== 인덱스 생성 =====
-- 캠페인별 미션 템플릿 조회 최적화
CREATE INDEX idx_mission_templates_campaign_id
  ON mission_templates(campaign_id);

-- 캠페인 내 미션 순서 정렬 최적화
CREATE INDEX idx_mission_templates_order
  ON mission_templates(campaign_id, "order");

-- ===== 코멘트 =====
COMMENT ON TABLE mission_templates IS '캠페인별 미션 템플릿';
COMMENT ON COLUMN mission_templates.campaign_id IS '연결된 캠페인 ID';
COMMENT ON COLUMN mission_templates.title IS '미션 제목';
COMMENT ON COLUMN mission_templates.description IS '미션 설명';
COMMENT ON COLUMN mission_templates."order" IS '미션 순서 (낮을수록 먼저 표시)';
COMMENT ON COLUMN mission_templates.verification_type IS '검증 방식: IMAGE(사진), QUIZ(퀴즈), TEXT_REVIEW(소감문), RPA_ACTION(자동화)';
COMMENT ON COLUMN mission_templates.reward_points IS '미션 완료 시 획득 포인트';
