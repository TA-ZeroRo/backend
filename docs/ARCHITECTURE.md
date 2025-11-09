# ZeroRo Backend Architecture - Database Design

## 📊 Database Schema Overview

ZeroRo 백엔드는 두 가지 미션 시스템을 지원합니다:
1. **Legacy Mission System** - 기존 단순 미션 시스템
2. **Campaign Agent System** - 신규 RPA 자동화 미션 시스템

---

## 🏗️ 데이터베이스 구조

### 1️⃣ Legacy Mission System (기존)

#### `mission` 테이블
```sql
CREATE TABLE mission (
  id SERIAL PRIMARY KEY,
  user_id UUID REFERENCES profiles(id),
  campaign_id INTEGER REFERENCES campaigns(id),
  status mission_status DEFAULT 'PROGRESS',
  started_at TIMESTAMPTZ DEFAULT NOW(),
  completed_at TIMESTAMPTZ,
  description TEXT
);
```

**용도:**
- 간단한 캠페인 참여 기록
- 캠페인 단위 진행 상황 추적
- 사용자가 캠페인 전체를 하나의 활동으로 수행

**관계:**
```
User (profiles) → mission ← Campaign (campaigns)
```

**현재 상태:**
- ✅ 프로덕션 사용 중 (1건의 데이터 존재)
- ✅ API 엔드포인트 활성화 (`/api/v1/mission/{user_id}`)
- ✅ 유지 및 계속 사용

---

### 2️⃣ Campaign Agent System (신규 🆕)

이 시스템은 **하나의 캠페인에 여러 개의 미션**을 정의하고, RPA로 자동화할 수 있는 고급 시스템입니다.

#### `mission_templates` 테이블
```sql
CREATE TABLE mission_templates (
  id BIGSERIAL PRIMARY KEY,
  campaign_id INTEGER REFERENCES campaigns(id) ON DELETE CASCADE,
  title TEXT NOT NULL,
  description TEXT,
  "order" INTEGER DEFAULT 0,
  verification_type TEXT CHECK (
    verification_type IN ('IMAGE', 'QUIZ', 'TEXT_REVIEW', 'RPA_ACTION')
  ),
  reward_points INTEGER DEFAULT 0,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);
```

**용도:**
- 캠페인별 미션 템플릿 정의
- 각 미션의 검증 방식 및 보상 포인트 설정
- 미션 순서 관리 (비순차적 진행 가능)

#### `mission_logs` 테이블
```sql
CREATE TABLE mission_logs (
  id BIGSERIAL PRIMARY KEY,
  user_id UUID REFERENCES profiles(id) ON DELETE CASCADE,
  mission_template_id BIGINT REFERENCES mission_templates(id) ON DELETE CASCADE,
  status TEXT CHECK (
    status IN ('IN_PROGRESS', 'PENDING_VERIFICATION', 'COMPLETED', 'FAILED')
  ),
  started_at TIMESTAMPTZ DEFAULT NOW(),
  completed_at TIMESTAMPTZ,
  proof_data JSONB,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW(),
  UNIQUE(user_id, mission_template_id)
);
```

**용도:**
- 사용자별 미션 진행 기록
- 검증 증거 저장 (JSONB: 이미지 URL, 퀴즈 답변 등)
- RPA 자동 제출 결과 저장

**관계:**
```
Campaign (campaigns)
    ↓ 1:N
mission_templates (미션 정의)
    ↓ 1:N
mission_logs (사용자별 진행 기록)
    ↓ N:1
User (profiles)
```

**특징:**
- ✅ 하나의 캠페인에 여러 미션 정의 가능
- ✅ 각 미션마다 다른 검증 방식
- ✅ 비순차적 진행 (순서 무관)
- ✅ RPA 자동화 지원 (설정 기반 Self-Healing)
- ✅ UNIQUE 제약조건으로 중복 방지

---

### 2️⃣-1 RPA System (Self-Healing) 🆕

Campaign Agent System의 RPA 자동화를 위한 설정 관리 시스템

#### `rpa_site_configs` 테이블
```sql
CREATE TABLE rpa_site_configs (
  id BIGSERIAL PRIMARY KEY,
  site_code TEXT UNIQUE NOT NULL,
  site_name TEXT NOT NULL,
  base_url TEXT NOT NULL,
  login_url TEXT NOT NULL,
  form_url TEXT,
  login_config JSONB NOT NULL,
  form_config JSONB NOT NULL,
  selector_strategies JSONB,
  field_mapping JSONB,
  is_active BOOLEAN DEFAULT true,
  last_verified_at TIMESTAMPTZ,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);
```

**용도:**
- RPA 사이트별 설정 중앙 관리
- CSS 셀렉터 및 Self-Healing 전략 저장
- 여러 캠페인에서 동일한 사이트 설정 재사용

**관계:**
```
mission_templates
    ↓ N:1
rpa_site_configs (사이트 설정)
```

**Self-Healing 동작 원리:**
1. `selector_strategies`에 우선순위별 여러 셀렉터 저장
2. RPA 실행 시 priority 순서대로 시도
3. 첫 번째 셀렉터 실패 시 자동으로 다음 전략 시도
4. HTML 구조 변경에도 자동 대응

**설정 예시:**
```json
{
  "selector_strategies": {
    "username_input": [
      {"selector": "#username", "priority": 1, "method": "id"},
      {"selector": "input[name='userId']", "priority": 2, "method": "name"},
      {"selector": ".login-input:first-child", "priority": 3, "method": "class"}
    ]
  }
}
```

---

## 🔄 두 시스템의 공존

### **언제 어느 시스템을 사용하나?**

#### **Legacy `mission` 테이블 사용 시:**
```
✅ 간단한 단일 활동 캠페인
✅ 빠른 개발 필요
✅ 복잡한 단계 불필요
✅ 기존 코드 유지

예시:
- "재활용 분리수거 챌린지" (사진 1장만 제출)
- "텀블러 사용 인증" (단순 참여 기록)
```

#### **Campaign Agent `mission_logs` 사용 시:**
```
✅ 다단계 미션으로 구성된 캠페인
✅ 각 미션마다 다른 검증 방식
✅ RPA 자동 제출 필요
✅ 개별 포인트 보상

예시:
- "에코마일리지 종합 프로그램"
  1. 재활용 인증 사진 (IMAGE, 100pt)
  2. 환경 퀴즈 (QUIZ, 50pt)
  3. 소감문 작성 (TEXT_REVIEW, 150pt)
  4. RPA 자동 신청 (RPA_ACTION, 200pt)
```

### **캠페인 타입 구분**

`campaigns` 테이블의 `submission_type` 컬럼으로 구분:

```sql
ALTER TABLE campaigns
  ADD COLUMN submission_type TEXT
  CHECK (submission_type IN ('RPA_FORM_SUBMIT', 'DIRECT_API', 'MANUAL_GUIDE'))
  DEFAULT 'MANUAL_GUIDE';
```

- `MANUAL_GUIDE`: Legacy `mission` 테이블 사용
- `RPA_FORM_SUBMIT`: Campaign Agent `mission_logs` 사용
- `DIRECT_API`: Campaign Agent `mission_logs` 사용

---

## 📦 코드 구조

### Legacy Mission System

```
app/
├── schemas/mission_schemas.py          # MissionResponse
├── repository/mission_repository.py    # MissionRepository
├── services/mission_service.py         # MissionService
└── api/v1/endpoints/mission.py         # GET /mission/{user_id}
```

### Campaign Agent System

```
app/
├── schemas/
│   ├── mission_template_schemas.py     # MissionTemplateCreate/Response
│   └── mission_log_schemas.py          # MissionLogCreate/Response
├── repository/
│   ├── mission_template_repository.py
│   └── mission_log_repository.py
├── services/
│   ├── rpa_core.py                     # submit_eco_mileage_form()
│   └── campaign_agent_service.py       # CampaignAgentService
└── api/v1/endpoints/
    └── (필요 시 추가)
```

---

## 🎯 마이그레이션 이력

Supabase에 적용된 마이그레이션:

1. **`20251106103238_create_mission_templates`** ✅
   - `mission_templates` 테이블 생성
   - 인덱스: campaign_id, (campaign_id, order)

2. **`20251106103309_create_mission_logs`** ✅
   - `mission_logs` 테이블 생성
   - 인덱스: user_id, mission_template_id, status
   - UNIQUE 제약조건: (user_id, mission_template_id)

3. **`20251106103336_add_submission_type_to_campaigns`** ✅
   - `campaigns.submission_type` 컬럼 추가

---

## 🔐 보안 고려사항

### RLS (Row Level Security) 권장 설정

#### Legacy `mission` 테이블
```sql
ALTER TABLE mission ENABLE ROW LEVEL SECURITY;

-- 사용자는 자신의 미션만 조회 가능
CREATE POLICY "Users can view own missions"
ON mission FOR SELECT
USING (auth.uid() = user_id);

-- 사용자는 자신의 미션만 생성/수정 가능
CREATE POLICY "Users can manage own missions"
ON mission FOR ALL
USING (auth.uid() = user_id);
```

#### Campaign Agent `mission_logs` 테이블
```sql
ALTER TABLE mission_logs ENABLE ROW LEVEL SECURITY;

-- 사용자는 자신의 미션 로그만 관리 가능
CREATE POLICY "Users can manage own mission logs"
ON mission_logs FOR ALL
USING (auth.uid() = user_id);
```

#### `mission_templates` 테이블
```sql
ALTER TABLE mission_templates ENABLE ROW LEVEL SECURITY;

-- 모든 사용자가 미션 템플릿 조회 가능
CREATE POLICY "Mission templates are viewable by everyone"
ON mission_templates FOR SELECT
USING (true);
```

---

## 📈 확장 계획

### Phase 1: 현재 상태 (완료 ✅)
- Legacy `mission` 유지
- Campaign Agent 시스템 구축
- RPA 핵심 로직 완성

### Phase 2: API 엔드포인트 추가 (예정)
- `POST /campaigns/{id}/start` - 캠페인 시작
- `GET /campaigns/{id}/progress` - 진행 상황 조회
- `POST /mission-logs/{id}/submit` - RPA 제출
- `POST /mission-logs/{id}/retry` - 재시도

### Phase 3: 데이터 마이그레이션 (선택)
- Legacy `mission` → `mission_logs` 마이그레이션 스크립트
- 데이터 정합성 검증
- 점진적 마이그레이션

---

## 🧪 테스트 데이터 생성

### 캠페인 + 미션 템플릿 생성
```sql
-- 캠페인 생성
INSERT INTO campaigns (title, description, host_organizer, campaign_url, submission_type, status)
VALUES ('에코마일리지 종합 프로그램', '다양한 환경 활동 참여', '서울시', 'https://eco.seoul.go.kr', 'RPA_FORM_SUBMIT', 'ACTIVE');

-- 미션 템플릿 생성
INSERT INTO mission_templates (campaign_id, title, description, "order", verification_type, reward_points)
VALUES
  (1, '재활용 인증 사진 올리기', '재활용품 분리수거 사진', 1, 'IMAGE', 100),
  (1, '환경 퀴즈 풀기', '환경 보호 퀴즈', 2, 'QUIZ', 50),
  (1, '활동 소감문 작성', '캠페인 소감', 3, 'TEXT_REVIEW', 150),
  (1, 'RPA 자동 신청', '에코마일리지 자동 제출', 4, 'RPA_ACTION', 200);
```

---

## 📚 참고 자료

- [Database Schema Documentation](./database.md)
- [Supabase MCP Integration](https://supabase.com/docs)
- [Playwright RPA Documentation](https://playwright.dev/)

---

**문서 버전:** 1.0
**최종 업데이트:** 2025-01-06
**작성자:** Claude (ZeroRo Backend Team)
