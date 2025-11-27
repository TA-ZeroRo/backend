-- Migration: Create recruiting and chat tables
-- Description: 캠페인 리크루팅 및 채팅 기능을 위한 테이블
-- Created: 2025-01-26

-- ===== recruiting_posts 테이블 생성 =====
CREATE TABLE IF NOT EXISTS recruiting_posts (
  id BIGSERIAL PRIMARY KEY,
  user_id UUID NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
  campaign_id INTEGER NOT NULL REFERENCES campaigns(id) ON DELETE CASCADE,
  title TEXT NOT NULL,
  region TEXT NOT NULL,
  city TEXT NOT NULL,
  capacity INTEGER NOT NULL CHECK (capacity > 0),
  current_members INTEGER NOT NULL DEFAULT 1 CHECK (current_members >= 0 AND current_members <= capacity),
  start_date DATE NOT NULL,
  end_date DATE,
  min_age INTEGER NOT NULL DEFAULT 0 CHECK (min_age >= 0),
  max_age INTEGER NOT NULL DEFAULT 0 CHECK (max_age >= 0),
  is_recruiting BOOLEAN NOT NULL DEFAULT true,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- ===== recruiting_chat_rooms 테이블 생성 =====
CREATE TABLE IF NOT EXISTS recruiting_chat_rooms (
  id BIGSERIAL PRIMARY KEY,
  recruiting_post_id BIGINT NOT NULL UNIQUE REFERENCES recruiting_posts(id) ON DELETE CASCADE,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ===== recruiting_chat_room_participants 테이블 생성 =====
CREATE TABLE IF NOT EXISTS recruiting_chat_room_participants (
  id BIGSERIAL PRIMARY KEY,
  chat_room_id BIGINT NOT NULL REFERENCES recruiting_chat_rooms(id) ON DELETE CASCADE,
  user_id UUID NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
  joined_at TIMESTAMPTZ DEFAULT NOW(),
  UNIQUE(chat_room_id, user_id)
);

-- ===== recruiting_chat_messages 테이블 생성 =====
CREATE TABLE IF NOT EXISTS recruiting_chat_messages (
  id BIGSERIAL PRIMARY KEY,
  chat_room_id BIGINT NOT NULL REFERENCES recruiting_chat_rooms(id) ON DELETE CASCADE,
  user_id UUID NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
  message TEXT NOT NULL,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ===== recruiting_posts 인덱스 생성 =====
-- 사용자별 리크루팅 게시글 조회 최적화
CREATE INDEX idx_recruiting_posts_user_id
  ON recruiting_posts(user_id);

-- 캠페인별 리크루팅 게시글 조회 최적화
CREATE INDEX idx_recruiting_posts_campaign_id
  ON recruiting_posts(campaign_id);

-- 모집 상태별 조회 최적화
CREATE INDEX idx_recruiting_posts_is_recruiting
  ON recruiting_posts(is_recruiting);

-- 지역별 조회 최적화
CREATE INDEX idx_recruiting_posts_region_city
  ON recruiting_posts(region, city);

-- 날짜 범위 조회 최적화
CREATE INDEX idx_recruiting_posts_start_date
  ON recruiting_posts(start_date);

-- ===== recruiting_chat_rooms 인덱스 생성 =====
-- 리크루팅 게시글로 채팅방 조회 최적화
CREATE INDEX idx_chat_rooms_recruiting_post_id
  ON recruiting_chat_rooms(recruiting_post_id);

-- ===== recruiting_chat_room_participants 인덱스 생성 =====
-- 채팅방별 참여자 조회 최적화
CREATE INDEX idx_chat_room_participants_room_id
  ON recruiting_chat_room_participants(chat_room_id);

-- 사용자별 참여 채팅방 조회 최적화
CREATE INDEX idx_chat_room_participants_user_id
  ON recruiting_chat_room_participants(user_id);

-- ===== recruiting_chat_messages 인덱스 생성 =====
-- 채팅방별 메시지 조회 최적화
CREATE INDEX idx_chat_messages_room_id_created_at
  ON recruiting_chat_messages(chat_room_id, created_at DESC);

-- 사용자별 메시지 조회 최적화
CREATE INDEX idx_chat_messages_user_id
  ON recruiting_chat_messages(user_id);

-- ===== 코멘트 =====
COMMENT ON TABLE recruiting_posts IS '캠페인 리크루팅 게시글';
COMMENT ON COLUMN recruiting_posts.user_id IS '게시글 작성자 UUID (주최자)';
COMMENT ON COLUMN recruiting_posts.campaign_id IS '연결된 캠페인 ID';
COMMENT ON COLUMN recruiting_posts.title IS '리크루팅 제목';
COMMENT ON COLUMN recruiting_posts.region IS '지역 (예: 서울특별시)';
COMMENT ON COLUMN recruiting_posts.city IS '도시 (예: 강남구)';
COMMENT ON COLUMN recruiting_posts.capacity IS '최대 참여 인원';
COMMENT ON COLUMN recruiting_posts.current_members IS '현재 참여 인원';
COMMENT ON COLUMN recruiting_posts.start_date IS '활동 시작 날짜';
COMMENT ON COLUMN recruiting_posts.end_date IS '활동 종료 날짜 (선택)';
COMMENT ON COLUMN recruiting_posts.min_age IS '최소 연령 (0이면 제한 없음)';
COMMENT ON COLUMN recruiting_posts.max_age IS '최대 연령 (0이면 제한 없음)';
COMMENT ON COLUMN recruiting_posts.is_recruiting IS '모집 중 여부';

COMMENT ON TABLE recruiting_chat_rooms IS '리크루팅 채팅방';
COMMENT ON COLUMN recruiting_chat_rooms.recruiting_post_id IS '연결된 리크루팅 게시글 ID';

COMMENT ON TABLE recruiting_chat_room_participants IS '채팅방 참여자 목록';
COMMENT ON COLUMN recruiting_chat_room_participants.chat_room_id IS '채팅방 ID';
COMMENT ON COLUMN recruiting_chat_room_participants.user_id IS '참여자 UUID';
COMMENT ON COLUMN recruiting_chat_room_participants.joined_at IS '참여 시간';

COMMENT ON TABLE recruiting_chat_messages IS '채팅 메시지';
COMMENT ON COLUMN recruiting_chat_messages.chat_room_id IS '채팅방 ID';
COMMENT ON COLUMN recruiting_chat_messages.user_id IS '메시지 작성자 UUID';
COMMENT ON COLUMN recruiting_chat_messages.message IS '메시지 내용';
