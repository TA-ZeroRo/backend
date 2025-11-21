# Database Migration History

## 🗂️ ZeroRo Backend 데이터베이스 마이그레이션 이력

---

## 2025-01-06: Campaign Agent System 구축 및 Legacy 시스템 제거

### 📦 적용된 마이그레이션

#### 1. `create_mission_templates` (20251106103238)
**목적**: 캠페인별 미션 템플릿 정의 시스템 구축

**변경사항**:
- ✅ `mission_templates` 테이블 생성
- ✅ 인덱스 2개 생성: `campaign_id`, `(campaign_id, order)`
- ✅ Foreign Key: `campaigns(id)` ON DELETE CASCADE

**테이블 구조**:
```sql
mission_templates
├── id (BIGSERIAL PK)
├── campaign_id (INTEGER FK)
├── title (TEXT)
├── description (TEXT)
├── order (INTEGER DEFAULT 0)
├── verification_type (TEXT CHECK)
├── reward_points (INTEGER CHECK >= 0)
├── created_at (TIMESTAMPTZ)
└── updated_at (TIMESTAMPTZ)
```

---

#### 2. `create_mission_logs` (20251106103309)
**목적**: 사용자별 미션 진행 로그 시스템 구축

**변경사항**:
- ✅ `mission_logs` 테이블 생성
- ✅ 인덱스 4개 생성: `user_id`, `mission_template_id`, `status`, UNIQUE(`user_id`, `mission_template_id`)
- ✅ Foreign Keys: `profiles(id)`, `mission_templates(id)` ON DELETE CASCADE

**테이블 구조**:
```sql
mission_logs
├── id (BIGSERIAL PK)
├── user_id (UUID FK)
├── mission_template_id (BIGINT FK)
├── status (TEXT CHECK)
├── started_at (TIMESTAMPTZ)
├── completed_at (TIMESTAMPTZ)
├── proof_data (JSONB)
├── created_at (TIMESTAMPTZ)
└── updated_at (TIMESTAMPTZ)
```

---

#### 3. `add_submission_type_to_campaigns` (20251106103336)
**목적**: 캠페인 제출 방식 구분

**변경사항**:
- ✅ `campaigns.submission_type` 컬럼 추가
- ✅ CHECK 제약조건: `RPA_FORM_SUBMIT`, `DIRECT_API`, `MANUAL_GUIDE`
- ✅ 기본값: `MANUAL_GUIDE`

---

#### 4. `migrate_mission_to_mission_logs` (20251106103400)
**목적**: Legacy mission 데이터를 새 시스템으로 마이그레이션

**변경사항**:
- ✅ campaign_id=2 (recycle)에 기본 `mission_template` 생성
- ✅ 기존 `mission` 레코드 1건 → `mission_logs`로 이전
- ✅ status 값 변환 (PROGRESS → IN_PROGRESS 등)
- ✅ description을 `proof_data` JSONB로 변환

**마이그레이션 상세**:
```sql
-- Before (mission 테이블)
{
  "id": 1,
  "user_id": "346b4ae4-ea3c-43c3-a9a8-5e5ccadd006f",
  "campaign_id": 2,
  "status": "PROGRESS",
  "description": "gd"
}

-- After (mission_logs 테이블)
{
  "id": 1,
  "user_id": "346b4ae4-ea3c-43c3-a9a8-5e5ccadd006f",
  "mission_template_id": 1,
  "status": "IN_PROGRESS",
  "proof_data": {
    "description": "gd",
    "migrated_from": "legacy_mission"
  }
}
```

---

#### 5. `drop_legacy_mission_table` (20251106103500)
**목적**: Legacy 시스템 완전 제거

**변경사항**:
- ✅ `mission` 테이블 DROP
- ✅ `mission_status` ENUM TYPE DROP
- ✅ Legacy 코드 파일 삭제:
  - `app/schemas/mission_schemas.py`
  - `app/repository/mission_repository.py`
  - `app/services/mission_service.py`
  - `app/api/v1/endpoints/mission.py`
- ✅ API 라우터에서 mission 엔드포인트 제거

---

## 🎯 마이그레이션 결과

### Before (Legacy System)
```
campaigns
    ↓
mission (사용자별 캠페인 참여 기록)
    ↓
profiles
```

### After (Campaign Agent System)
```
campaigns
    ↓
mission_templates (캠페인별 미션 정의)
    ↓
mission_logs (사용자별 미션 진행 로그)
    ↓
profiles
```

---

## 📊 데이터 이전 현황

| 테이블 | Before | After | Status |
|--------|--------|-------|--------|
| `mission` | 1건 | 삭제됨 | ✅ 완료 |
| `mission_templates` | - | 1건 생성 | ✅ 완료 |
| `mission_logs` | - | 1건 생성 | ✅ 완료 |

---

## 🔄 롤백 가이드

만약 문제가 발생하여 롤백이 필요한 경우:

### Step 1: mission 테이블 재생성
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

CREATE TYPE mission_status AS ENUM ('PROGRESS', 'VERIFICATION', 'COMPLETED', 'FAILED');
```

### Step 2: mission_logs에서 mission으로 데이터 복원
```sql
INSERT INTO mission (user_id, campaign_id, status, started_at, completed_at, description)
SELECT
  ml.user_id,
  mt.campaign_id,
  CASE
    WHEN ml.status = 'IN_PROGRESS' THEN 'PROGRESS'
    WHEN ml.status = 'PENDING_VERIFICATION' THEN 'VERIFICATION'
    WHEN ml.status = 'COMPLETED' THEN 'COMPLETED'
    WHEN ml.status = 'FAILED' THEN 'FAILED'
  END::mission_status,
  ml.started_at,
  ml.completed_at,
  ml.proof_data->>'description'
FROM mission_logs ml
JOIN mission_templates mt ON ml.mission_template_id = mt.id
WHERE ml.proof_data->>'migrated_from' = 'legacy_mission';
```

### Step 3: Git에서 삭제된 코드 복원
```bash
git checkout HEAD~1 -- app/schemas/mission_schemas.py
git checkout HEAD~1 -- app/repository/mission_repository.py
git checkout HEAD~1 -- app/services/mission_service.py
git checkout HEAD~1 -- app/api/v1/endpoints/mission.py
```

---

## ⚠️ Breaking Changes

### API 엔드포인트 변경
```
❌ DELETE: GET /api/v1/mission/{user_id}

✅ 추가 예정:
- POST /api/v1/campaigns/{id}/start
- GET /api/v1/campaigns/{id}/progress?user_id={uuid}
- POST /api/v1/mission-logs/{id}/submit
- POST /api/v1/mission-logs/{id}/retry
```

### 프론트엔드 영향
- Legacy mission API 호출하던 코드 수정 필요
- 새로운 Campaign Agent API 사용 필요

---

## 🚀 다음 단계

### Phase 1: API 구현 (진행 필요)
- [ ] `POST /api/v1/campaigns/{id}/start` - 캠페인 시작
- [ ] `GET /api/v1/campaigns/{id}/progress` - 진행 상황 조회
- [ ] `POST /api/v1/mission-logs/{id}/submit` - RPA 제출
- [ ] `POST /api/v1/mission-logs/{id}/retry` - 재시도

### Phase 2: 프론트엔드 연동
- [ ] 새 API 스펙 공유
- [ ] 프론트엔드 코드 수정
- [ ] 통합 테스트

### Phase 3: 모니터링
- [ ] 새 시스템 안정성 확인
- [ ] 성능 모니터링
- [ ] 사용자 피드백 수집

---

## 📚 관련 문서

- [Architecture Documentation](./ARCHITECTURE.md) - 전체 아키텍처 설명
- [Mission Systems Comparison](./MISSION_SYSTEMS_COMPARISON.md) - 두 시스템 비교 (삭제 예정)
- [Database Schema](./database.md) - 전체 데이터베이스 스키마

---

## 📝 참고사항

### 의사결정 이유
- ✅ 두 시스템 공존 시 복잡도 증가
- ✅ 유지보수 부담 감소
- ✅ 단일 시스템으로 통일하여 확장성 확보
- ✅ Legacy 데이터는 1건뿐이라 마이그레이션 부담 낮음

### 위험 완화 전략
- ✅ 데이터 마이그레이션 전 백업
- ✅ 단계별 마이그레이션 (템플릿 생성 → 데이터 이전 → 테이블 삭제)
- ✅ 롤백 가이드 작성

---

**문서 버전:** 1.0
**최종 업데이트:** 2025-01-06
**작성자:** Claude (ZeroRo Backend Team)
