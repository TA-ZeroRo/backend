-- Migration: Create mission_logs table
-- Description: 사용자별 미션 진행 로그 및 검증 데이터
-- Created: 2025-01-06

-- ===== mission_logs 테이블 생성 =====
CREATE TABLE IF NOT EXISTS mission_logs (
  id BIGSERIAL PRIMARY KEY,
  user_id UUID NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
  mission_template_id BIGINT NOT NULL REFERENCES mission_templates(id) ON DELETE CASCADE,
  status TEXT NOT NULL DEFAULT 'IN_PROGRESS' CHECK (
    status IN ('IN_PROGRESS', 'PENDING_VERIFICATION', 'COMPLETED', 'FAILED')
  ),
  started_at TIMESTAMPTZ DEFAULT NOW(),
  completed_at TIMESTAMPTZ,
  proof_data JSONB,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- ===== 인덱스 생성 =====
-- 사용자별 미션 로그 조회 최적화
CREATE INDEX idx_mission_logs_user_id
  ON mission_logs(user_id);

-- 미션 템플릿별 로그 조회 최적화
CREATE INDEX idx_mission_logs_template_id
  ON mission_logs(mission_template_id);

-- 상태별 미션 조회 최적화
CREATE INDEX idx_mission_logs_status
  ON mission_logs(status);

-- 사용자-템플릿 조합 중복 방지 (한 사용자는 한 미션에 하나의 로그만)
CREATE UNIQUE INDEX idx_mission_logs_user_template
  ON mission_logs(user_id, mission_template_id);

-- ===== 코멘트 =====
COMMENT ON TABLE mission_logs IS '사용자별 미션 진행 로그';
COMMENT ON COLUMN mission_logs.user_id IS '사용자 UUID';
COMMENT ON COLUMN mission_logs.mission_template_id IS '미션 템플릿 ID';
COMMENT ON COLUMN mission_logs.status IS '미션 상태: IN_PROGRESS(진행중), PENDING_VERIFICATION(검증대기), COMPLETED(완료), FAILED(실패)';
COMMENT ON COLUMN mission_logs.started_at IS '미션 시작 시간';
COMMENT ON COLUMN mission_logs.completed_at IS '미션 완료 시간';
COMMENT ON COLUMN mission_logs.proof_data IS '검증 증거 데이터 (JSON): 이미지 URL, 퀴즈 답변 등';
