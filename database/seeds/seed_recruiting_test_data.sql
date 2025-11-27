-- =============================================
-- 리크루팅 채팅 테스트 데이터 시드
-- Supabase Dashboard > SQL Editor 에서 실행
-- =============================================

-- 실제 profiles 및 campaigns 데이터 기반으로 생성됨
-- 생성일: 2025-01-26

-- =============================================
-- 1. 리크루팅 게시글 생성
-- =============================================
-- 실제 프로필:
--   hong (df74fb34-...) - 부산광역시 서구
--   jojo (1257a147-...) - 서울특별시 성북구
--   보리보리쌀 (2d8ece54-...) - 경기도 고양시
--   Zeroro Dev (346b4ae4-...) - 경기도 파주시
--   seol (e5c77b27-...) - 경기도 고양시

-- 실제 캠페인:
--   23: 등촌1종합사회복지관 플로깅 '줍줍이들' (서울, OFFLINE)
--   24: 제주형 2인1조 장소무제한 플로깅 (제주, OFFLINE)
--   34: 치악산국립공원 탐방로 환경정화 봉사 (강원도, OFFLINE)

INSERT INTO recruiting_posts (id, user_id, campaign_id, title, region, city, capacity, current_members, start_date, end_date, min_age, max_age, is_recruiting)
VALUES
  (1, 'df74fb34-da5f-4e0d-9aa9-32133b8937e4', 23, '이번 주말 등촌동에서 플로깅 함께해요!', '서울특별시', '강서구', 4, 2, '2025-02-01', '2025-02-01', 20, 40, true),
  (2, '1257a147-80ae-4d71-aab9-e8474a6e6bc9', 24, '제주도 플로깅 여행 같이 가실 분!', '제주특별자치도', '제주시', 6, 3, '2025-02-15', '2025-02-16', 25, 35, true),
  (3, '2d8ece54-6cd1-45d1-ba9a-232944082013', 34, '치악산 등산하면서 환경정화 봉사해요', '강원도', '원주시', 8, 1, '2025-02-22', '2025-02-22', 0, 0, true)
ON CONFLICT (id) DO UPDATE SET
  title = EXCLUDED.title,
  current_members = EXCLUDED.current_members;

-- 시퀀스 업데이트 (ID 충돌 방지)
SELECT setval('recruiting_posts_id_seq', (SELECT MAX(id) FROM recruiting_posts));

-- =============================================
-- 2. 채팅방 생성
-- =============================================
INSERT INTO recruiting_chat_rooms (id, recruiting_post_id)
VALUES
  (1, 1),
  (2, 2),
  (3, 3)
ON CONFLICT (recruiting_post_id) DO NOTHING;

-- 시퀀스 업데이트
SELECT setval('recruiting_chat_rooms_id_seq', (SELECT MAX(id) FROM recruiting_chat_rooms));

-- =============================================
-- 3. 채팅방 참여자 추가
-- =============================================
-- 채팅방 1: hong(주최자), jojo
INSERT INTO recruiting_chat_room_participants (chat_room_id, user_id)
VALUES
  (1, 'df74fb34-da5f-4e0d-9aa9-32133b8937e4'),
  (1, '1257a147-80ae-4d71-aab9-e8474a6e6bc9')
ON CONFLICT (chat_room_id, user_id) DO NOTHING;

-- 채팅방 2: jojo(주최자), hong, 보리보리쌀, seol
INSERT INTO recruiting_chat_room_participants (chat_room_id, user_id)
VALUES
  (2, '1257a147-80ae-4d71-aab9-e8474a6e6bc9'),
  (2, 'df74fb34-da5f-4e0d-9aa9-32133b8937e4'),
  (2, '2d8ece54-6cd1-45d1-ba9a-232944082013'),
  (2, 'e5c77b27-0042-4611-b19f-027ef9a495aa')
ON CONFLICT (chat_room_id, user_id) DO NOTHING;

-- 채팅방 3: 보리보리쌀(주최자), Zeroro Dev
INSERT INTO recruiting_chat_room_participants (chat_room_id, user_id)
VALUES
  (3, '2d8ece54-6cd1-45d1-ba9a-232944082013'),
  (3, '346b4ae4-ea3c-43c3-a9a8-5e5ccadd006f')
ON CONFLICT (chat_room_id, user_id) DO NOTHING;

-- =============================================
-- 4. 채팅 메시지 추가
-- =============================================
-- 채팅방 1 메시지 (등촌동 플로깅)
INSERT INTO recruiting_chat_messages (chat_room_id, user_id, message, created_at)
VALUES
  (1, 'df74fb34-da5f-4e0d-9aa9-32133b8937e4', '안녕하세요! 등촌동 플로깅 모집글 올린 hong입니다', NOW() - INTERVAL '2 hours'),
  (1, '1257a147-80ae-4d71-aab9-e8474a6e6bc9', '안녕하세요! 서울에서 참여하고 싶어서 신청했어요~', NOW() - INTERVAL '1 hour 50 minutes'),
  (1, 'df74fb34-da5f-4e0d-9aa9-32133b8937e4', '환영합니다! 토요일 오전 10시에 등촌역 2번 출구에서 만나요', NOW() - INTERVAL '1 hour 45 minutes'),
  (1, '1257a147-80ae-4d71-aab9-e8474a6e6bc9', '네! 장갑이나 집게는 준비해가야 할까요?', NOW() - INTERVAL '1 hour 30 minutes'),
  (1, 'df74fb34-da5f-4e0d-9aa9-32133b8937e4', '복지관에서 제공해준다고 해요! 편하게 오시면 됩니다', NOW() - INTERVAL '1 hour 20 minutes'),
  (1, '1257a147-80ae-4d71-aab9-e8474a6e6bc9', '감사합니다! 그럼 토요일에 봬요~', NOW() - INTERVAL '1 hour');

-- 채팅방 2 메시지 (제주도 플로깅 여행)
INSERT INTO recruiting_chat_messages (chat_room_id, user_id, message, created_at)
VALUES
  (2, '1257a147-80ae-4d71-aab9-e8474a6e6bc9', '제주도 플로깅 여행 관심있으신 분들 환영합니다!', NOW() - INTERVAL '3 hours'),
  (2, 'df74fb34-da5f-4e0d-9aa9-32133b8937e4', '오 제주도 플로깅이라니 좋네요! 저도 참여하고 싶어요', NOW() - INTERVAL '2 hours 50 minutes'),
  (2, '2d8ece54-6cd1-45d1-ba9a-232944082013', '안녕하세요~ 고양시에서 왔어요. 저도 함께해도 될까요?', NOW() - INTERVAL '2 hours 30 minutes'),
  (2, 'e5c77b27-0042-4611-b19f-027ef9a495aa', '저도 끼워주세요! seol입니다', NOW() - INTERVAL '2 hours 20 minutes'),
  (2, '1257a147-80ae-4d71-aab9-e8474a6e6bc9', '네 모두 환영합니다! 제주공항에서 만나서 렌트카로 이동할 예정이에요', NOW() - INTERVAL '2 hours'),
  (2, 'df74fb34-da5f-4e0d-9aa9-32133b8937e4', '숙소는 어디로 잡으셨나요?', NOW() - INTERVAL '1 hour 50 minutes'),
  (2, '1257a147-80ae-4d71-aab9-e8474a6e6bc9', '제주시 쪽 게스트하우스 예약했어요. 1박 3만원 정도입니다', NOW() - INTERVAL '1 hour 40 minutes'),
  (2, '2d8ece54-6cd1-45d1-ba9a-232944082013', '좋아요! 저도 같은 곳으로 예약할게요', NOW() - INTERVAL '1 hour 30 minutes'),
  (2, 'e5c77b27-0042-4611-b19f-027ef9a495aa', '저도요! 기대되네요 ㅎㅎ', NOW() - INTERVAL '1 hour 20 minutes');

-- 채팅방 3 메시지 (치악산 환경정화)
INSERT INTO recruiting_chat_messages (chat_room_id, user_id, message, created_at)
VALUES
  (3, '2d8ece54-6cd1-45d1-ba9a-232944082013', '치악산 등산하면서 환경정화 봉사 함께하실 분 구해요!', NOW() - INTERVAL '1 hour'),
  (3, '346b4ae4-ea3c-43c3-a9a8-5e5ccadd006f', '안녕하세요! Zeroro Dev입니다. 개발자인데 주말에 자연도 좀 보고 싶어서요', NOW() - INTERVAL '45 minutes'),
  (3, '2d8ece54-6cd1-45d1-ba9a-232944082013', '오 환영합니다! 저도 평일엔 재택근무라 주말엔 밖에 나가고 싶더라고요', NOW() - INTERVAL '40 minutes'),
  (3, '346b4ae4-ea3c-43c3-a9a8-5e5ccadd006f', '맞아요 ㅎㅎ 등산 난이도는 어느 정도인가요?', NOW() - INTERVAL '35 minutes'),
  (3, '2d8ece54-6cd1-45d1-ba9a-232944082013', '비로봉 코스로 갈 건데 중급 정도예요. 4시간 정도 소요됩니다', NOW() - INTERVAL '30 minutes'),
  (3, '346b4ae4-ea3c-43c3-a9a8-5e5ccadd006f', '좋아요! 준비물은 뭐가 필요할까요?', NOW() - INTERVAL '25 minutes'),
  (3, '2d8ece54-6cd1-45d1-ba9a-232944082013', '등산화, 물, 간식 정도면 될 것 같아요. 쓰레기봉투는 제가 챙겨갈게요', NOW() - INTERVAL '20 minutes');

-- =============================================
-- 5. 데이터 확인
-- =============================================
SELECT 'recruiting_posts' as table_name, COUNT(*) as count FROM recruiting_posts
UNION ALL
SELECT 'recruiting_chat_rooms', COUNT(*) FROM recruiting_chat_rooms
UNION ALL
SELECT 'recruiting_chat_room_participants', COUNT(*) FROM recruiting_chat_room_participants
UNION ALL
SELECT 'recruiting_chat_messages', COUNT(*) FROM recruiting_chat_messages;
