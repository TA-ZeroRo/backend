-- Seed: Campaign 3 Mission Templates
-- Description: 제로서울챌린지 캠페인의 3개 미션 템플릿
-- Created: 2025-01-10

-- ===== Campaign 3: 제로서울챌린지 미션 템플릿 =====
INSERT INTO mission_templates (
  campaign_id,
  title,
  description,
  "order",
  verification_type,
  reward_points
) VALUES
-- Mission 1: 일회용품 제로 챌린지
(
  3,
  '일회용품 제로 챌린지',
  '하루 동안 일회용품 대신 다회용품(텀블러, 에코백 등) 사용 후, 인증사진을 개인 SNS에 해시태그(#제로서울챌린지)와 함께 업로드',
  1,
  'IMAGE',
  100
),

-- Mission 2: 분리배출 실천 인증
(
  3,
  '분리배출 실천 인증',
  '가정에서 쓰레기 분리배출 완료 후, 분리된 쓰레기의 종류와 분리과정 사진을 인증',
  2,
  'IMAGE',
  100
),

-- Mission 3: 미세먼지 줄이기 실천
(
  3,
  '미세먼지 줄이기 실천',
  '실내외 환기, 공기정화 식물 관리, 친환경 이동수단(자전거, 대중교통) 이용 모습 인증사진 제출',
  3,
  'IMAGE',
  100
)
ON CONFLICT (id) DO NOTHING;

-- ===== 확인 쿼리 =====
SELECT
  id,
  campaign_id,
  title,
  "order",
  verification_type,
  reward_points,
  created_at
FROM mission_templates
WHERE campaign_id = 3
ORDER BY "order" ASC;
