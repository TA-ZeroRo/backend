-- 캠페인 보상 발송 추적 테이블
-- 캠페인별로 승인된 유저에게 보상을 발송했는지 추적

CREATE TABLE IF NOT EXISTS campaign_reward_tracking (
    id BIGSERIAL PRIMARY KEY,
    campaign_id INTEGER NOT NULL REFERENCES campaigns(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
    reward_sent BOOLEAN DEFAULT FALSE,
    sent_at TIMESTAMPTZ,
    note TEXT, -- 메모 (어떤 보상을 보냈는지 등)
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),

    -- 캠페인당 유저는 한 번만 등록
    UNIQUE(campaign_id, user_id)
);

-- 인덱스
CREATE INDEX IF NOT EXISTS idx_campaign_reward_tracking_campaign_id ON campaign_reward_tracking(campaign_id);
CREATE INDEX IF NOT EXISTS idx_campaign_reward_tracking_user_id ON campaign_reward_tracking(user_id);
CREATE INDEX IF NOT EXISTS idx_campaign_reward_tracking_reward_sent ON campaign_reward_tracking(reward_sent);

-- RLS 정책
ALTER TABLE campaign_reward_tracking ENABLE ROW LEVEL SECURITY;

-- 파트너는 자신의 캠페인에 대한 보상 추적만 조회/수정 가능
CREATE POLICY "Partners can manage their campaign reward tracking"
    ON campaign_reward_tracking
    FOR ALL
    USING (
        campaign_id IN (
            SELECT c.id FROM campaigns c
            JOIN partners p ON c.partner_id = p.id
            WHERE p.user_id = auth.uid()
        )
    );

-- Service role은 모든 접근 가능
CREATE POLICY "Service role full access to campaign_reward_tracking"
    ON campaign_reward_tracking
    FOR ALL
    USING (auth.role() = 'service_role');

COMMENT ON TABLE campaign_reward_tracking IS '캠페인 보상 발송 추적 테이블';
COMMENT ON COLUMN campaign_reward_tracking.reward_sent IS '보상 발송 여부';
COMMENT ON COLUMN campaign_reward_tracking.sent_at IS '보상 발송 시간';
COMMENT ON COLUMN campaign_reward_tracking.note IS '보상 관련 메모';
