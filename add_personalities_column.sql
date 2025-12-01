-- Migration: add_personalities_column_to_profiles
-- Created: 2025-12-01
-- Description: profiles 테이블에 보유한 성격 목록을 저장하는 personalities 컬럼 추가

-- 1. personalities 컬럼 추가 (TEXT 배열 타입)
ALTER TABLE profiles
  ADD COLUMN IF NOT EXISTS personalities TEXT[] DEFAULT '{}';

-- 2. Index 생성 (성격 검색 최적화)
CREATE INDEX IF NOT EXISTS idx_profiles_personalities
  ON profiles USING GIN (personalities);

-- 3. 컬럼 설명 추가
COMMENT ON COLUMN profiles.personalities IS '사용자가 보유한 성격 ID 목록 (예: friendly, playful, researcher, coach, elegant)';

-- 4. 기존 사용자에게 기본 성격(friendly) 자동 부여 (선택사항)
-- UPDATE profiles
-- SET personalities = ARRAY['friendly']
-- WHERE personalities = '{}' OR personalities IS NULL;

-- 참고: 사용 가능한 성격 목록
-- - friendly: 친절하고 부드러운
-- - playful: 텐션 높은 장난꾸러기
-- - researcher: 연구원 느낌
-- - coach: 동기부여하는 코치
-- - elegant: 느긋하면서 품격있는
