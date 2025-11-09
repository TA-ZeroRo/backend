# Database Migrations

이 디렉토리는 ZeroRo Backend의 데이터베이스 스키마 변경 이력을 관리합니다.

## 📂 파일 구조

```
database/
└── migrations/
    ├── 001_create_mission_templates.sql
    ├── 002_create_mission_logs.sql
    ├── 003_add_submission_type_to_campaigns.sql
    └── README.md
```

## 🚀 마이그레이션 실행 방법

### 방법 1: Supabase 대시보드 (권장)

1. [Supabase Dashboard](https://supabase.com/dashboard) 접속
2. 프로젝트 선택
3. 왼쪽 메뉴에서 **SQL Editor** 클릭
4. 마이그레이션 파일 내용을 복사하여 붙여넣기
5. **실행 순서대로** 001 → 002 → 003 순서로 실행
6. **Run** 버튼 클릭

### 방법 2: psql 명령줄 (로컬/원격)

```bash
# 환경 변수에서 DATABASE_URL 설정 확인
echo $DATABASE_URL

# 마이그레이션 실행 (순서대로)
psql $DATABASE_URL -f database/migrations/001_create_mission_templates.sql
psql $DATABASE_URL -f database/migrations/002_create_mission_logs.sql
psql $DATABASE_URL -f database/migrations/003_add_submission_type_to_campaigns.sql
```

### 방법 3: Supabase CLI (추후 도입 시)

```bash
# Supabase CLI로 마이그레이션 적용
supabase db reset  # 로컬 환경
supabase db push   # 프로덕션 환경
```

## 📝 마이그레이션 파일 설명

### 001_create_mission_templates.sql
**목적**: 캠페인별 미션 템플릿 테이블 생성

**주요 내용**:
- `mission_templates` 테이블 생성
- 캠페인과 1:N 관계
- 검증 타입: IMAGE, QUIZ, TEXT_REVIEW, RPA_ACTION
- 순서(order) 및 포인트(reward_points) 관리

**테이블 구조**:
```sql
mission_templates
├── id (BIGSERIAL PK)
├── campaign_id (FK to campaigns)
├── title
├── description
├── order
├── verification_type
├── reward_points
├── created_at
└── updated_at
```

### 002_create_mission_logs.sql
**목적**: 사용자별 미션 진행 로그 테이블 생성

**주요 내용**:
- `mission_logs` 테이블 생성
- 사용자(profiles)와 미션 템플릿 연결
- 미션 상태: IN_PROGRESS, PENDING_VERIFICATION, COMPLETED, FAILED
- 검증 증거(proof_data) JSONB 저장

**테이블 구조**:
```sql
mission_logs
├── id (BIGSERIAL PK)
├── user_id (FK to profiles)
├── mission_template_id (FK to mission_templates)
├── status
├── started_at
├── completed_at
├── proof_data (JSONB)
├── created_at
└── updated_at
```

**중요**: `user_id`와 `mission_template_id` 조합에 UNIQUE 제약조건 있음 (중복 방지)

### 003_add_submission_type_to_campaigns.sql
**목적**: 캠페인 제출 방식 컬럼 추가

**주요 내용**:
- `campaigns` 테이블에 `submission_type` 컬럼 추가
- 제출 방식: RPA_FORM_SUBMIT, DIRECT_API, MANUAL_GUIDE
- 기본값: MANUAL_GUIDE

## 🔄 롤백 (Rollback)

마이그레이션을 되돌려야 할 경우:

### 003 롤백
```sql
ALTER TABLE campaigns DROP COLUMN IF EXISTS submission_type;
```

### 002 롤백
```sql
DROP TABLE IF EXISTS mission_logs;
```

### 001 롤백
```sql
DROP TABLE IF EXISTS mission_templates;
```

**주의**: 롤백 시 **역순**으로 실행해야 합니다 (003 → 002 → 001)

## ✅ 마이그레이션 확인

마이그레이션이 성공적으로 적용되었는지 확인:

```sql
-- 테이블 존재 확인
SELECT table_name
FROM information_schema.tables
WHERE table_schema = 'public'
  AND table_name IN ('mission_templates', 'mission_logs');

-- 테이블 구조 확인
\d mission_templates
\d mission_logs

-- campaigns 테이블에 submission_type 컬럼 확인
\d campaigns
```

## 📊 ER Diagram

```
campaigns (기존)
    ↓ 1:N (campaign_id)
mission_templates (신규)
    ↓ 1:N (mission_template_id)
mission_logs (신규)
    ↓ N:1 (user_id)
profiles (기존)
```

## 🔐 RLS (Row Level Security) 설정

마이그레이션 후 필요한 RLS 정책 (선택):

```sql
-- mission_templates: 모두 조회 가능
ALTER TABLE mission_templates ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Mission templates are viewable by everyone"
ON mission_templates FOR SELECT
USING (true);

-- mission_logs: 자신의 로그만 관리 가능
ALTER TABLE mission_logs ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Users can manage own mission logs"
ON mission_logs FOR ALL
USING (auth.uid() = user_id);
```

## 📦 테스트 데이터

마이그레이션 후 테스트 데이터 삽입 예시:

```sql
-- 미션 템플릿 생성
INSERT INTO mission_templates (campaign_id, title, description, "order", verification_type, reward_points)
VALUES
  (1, '재활용 인증 사진 올리기', '재활용품을 분리수거한 사진을 업로드하세요', 1, 'IMAGE', 100),
  (1, '환경 퀴즈 풀기', '환경 보호 퀴즈를 풀고 지식을 쌓으세요', 2, 'QUIZ', 50),
  (1, '활동 소감문 작성', '이번 캠페인 활동 소감을 작성해주세요', 3, 'TEXT_REVIEW', 150);

-- 미션 로그 생성 (user_id는 실제 UUID로 교체)
INSERT INTO mission_logs (user_id, mission_template_id, status, proof_data)
VALUES
  ('00000000-0000-0000-0000-000000000001', 1, 'COMPLETED', '{"image_url": "https://example.com/image.jpg"}'),
  ('00000000-0000-0000-0000-000000000001', 2, 'IN_PROGRESS', null);
```

## 🛠️ 트러블슈팅

### 문제: Foreign Key 에러
```
ERROR: insert or update on table "mission_templates" violates foreign key constraint
```

**해결**: `campaigns` 테이블에 해당 `campaign_id`가 존재하는지 확인

### 문제: UNIQUE 제약조건 위반
```
ERROR: duplicate key value violates unique constraint "idx_mission_logs_user_template"
```

**해결**: 해당 사용자는 이미 해당 미션에 대한 로그가 있습니다. UPDATE를 사용하세요.

## 📚 관련 파일

- **Pydantic 스키마**:
  - `app/schemas/mission_template_schemas.py`
  - `app/schemas/mission_log_schemas.py`
  - `app/schemas/campaign_schemas.py`

- **Repository**:
  - `app/repository/mission_template_repository.py`
  - `app/repository/mission_log_repository.py`

## 🔗 참고 자료

- [Supabase SQL Editor](https://supabase.com/docs/guides/database/overview#the-sql-editor)
- [PostgreSQL Data Types](https://www.postgresql.org/docs/current/datatype.html)
- [Supabase RLS Guide](https://supabase.com/docs/guides/auth/row-level-security)
