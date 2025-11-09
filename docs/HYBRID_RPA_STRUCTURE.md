# Hybrid RPA 구조 문서

## 📋 개요

**하이브리드 RPA 구조**는 로그인 설정은 사이트별로 공유하고, 폼 설정은 캠페인별로 개별 관리하는 유연한 RPA 시스템입니다.

**핵심 아이디어**:
- **로그인**: 같은 사이트 = 같은 로그인 → `rpa_site_configs` 테이블 (공유)
- **폼**: 같은 사이트라도 캠페인마다 다른 폼 → `campaigns` 테이블 (개별)

---

## 🏗️ 데이터베이스 구조

### 1. `rpa_site_configs` 테이블 (로그인 설정 - 공유)

```sql
CREATE TABLE rpa_site_configs (
  id BIGSERIAL PRIMARY KEY,
  site_code TEXT UNIQUE NOT NULL,           -- 'seoul_ecomileage'
  site_name TEXT NOT NULL,                  -- '서울시 에코마일리지'
  base_url TEXT NOT NULL,
  login_url TEXT NOT NULL,

  -- 로그인 설정만 (여러 Campaign이 재사용)
  login_config JSONB NOT NULL,              -- {"selectors": {"username_input": "#username", ...}}
  login_selector_strategies JSONB,          -- Self-Healing 전략 (로그인용)

  is_active BOOLEAN DEFAULT true,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);
```

**역할**: 사이트별 로그인 설정 라이브러리

**예시**:
```json
{
  "id": 1,
  "site_code": "seoul_ecomileage",
  "site_name": "서울시 에코마일리지",
  "base_url": "https://ecomileage.seoul.go.kr",
  "login_url": "https://ecomileage.seoul.go.kr/login",
  "login_config": {
    "selectors": {
      "username_input": "#username",
      "password_input": "#password",
      "submit_button": "button[type='submit']",
      "error_message": ".login-error"
    }
  },
  "login_selector_strategies": {
    "username_input": [
      {"selector": "#username", "priority": 1, "method": "id"},
      {"selector": "input[name='username']", "priority": 2, "method": "name"}
    ]
  }
}
```

---

### 2. `campaigns` 테이블 (폼 설정 - 개별)

```sql
ALTER TABLE campaigns
ADD COLUMN rpa_site_config_id BIGINT REFERENCES rpa_site_configs(id) ON DELETE SET NULL,
ADD COLUMN rpa_form_url TEXT,
ADD COLUMN rpa_form_config JSONB,
ADD COLUMN rpa_field_mapping JSONB,
ADD COLUMN rpa_form_selector_strategies JSONB;
```

**역할**: 캠페인별 폼 설정

**예시**:
```json
{
  "id": 10,
  "title": "서울시 에코마일리지 - 대중교통 이용",
  "rpa_site_config_id": 1,  // ← seoul_ecomileage 로그인 사용
  "rpa_form_url": "https://ecomileage.seoul.go.kr/apply/transit",
  "rpa_form_config": {
    "selectors": {
      "transport_type": "#transport_type",
      "usage_date": "#usage_date",
      "distance": "input[name='distance']",
      "submit_button": "#submit-button",
      "success_message": ".success-message"
    }
  },
  "rpa_field_mapping": {
    "user_transport": "transport_type",
    "user_date": "usage_date",
    "user_distance": "distance"
  },
  "rpa_form_selector_strategies": {
    "transport_type": [
      {"selector": "#transport_type", "priority": 1},
      {"selector": "select[name='type']", "priority": 2}
    ]
  }
}
```

---

## 🔄 데이터 흐름

### 실제 사용 시나리오

```
사용자: "서울시 에코마일리지 - 대중교통 이용" 캠페인 참여
   ↓
1. Campaign 조회 (id: 10)
   - rpa_site_config_id: 1
   - rpa_form_url: https://ecomileage.seoul.go.kr/apply/transit
   - rpa_form_config: {...}
   ↓
2. RPA Site Config 조회 (id: 1)
   - site_code: seoul_ecomileage
   - login_url: https://ecomileage.seoul.go.kr/login
   - login_config: {...}
   ↓
3. SelfHealingAdapter 초기화
   - login_config (공통)
   - form_config (Campaign별)
   ↓
4. 로그인 (공통 설정 사용)
   - Navigate to: login_url
   - Use: login_config, login_selector_strategies
   ↓
5. 폼 제출 (Campaign별 설정 사용)
   - Navigate to: rpa_form_url
   - Use: rpa_form_config, rpa_form_selector_strategies
   ↓
6. 결과 반환
```

---

## 💻 코드 예시

### 1. SelfHealingAdapter 초기화 (하이브리드)

```python
from app.services.rpa_adapters.base import SelfHealingAdapter

adapter = SelfHealingAdapter(
    page=page,
    login_config=site_config['login_config'],               # 공통
    login_strategies=site_config.get('login_selector_strategies'),  # 공통
    form_config=campaign['rpa_form_config'],                # Campaign별
    form_strategies=campaign.get('rpa_form_selector_strategies'),   # Campaign별
    field_mapping=campaign.get('rpa_field_mapping', {})     # Campaign별
)
```

### 2. RPA 실행 (CampaignAgentService)

```python
# Campaign 조회
campaign = await self.campaign_repo.get_campaign_by_id(template['campaign_id'])

# 하이브리드 RPA 실행
if campaign.get('rpa_site_config_id') and campaign.get('rpa_form_config'):
    # 로그인 설정 조회
    site_config = await self.rpa_config_repo.get_by_id(
        campaign['rpa_site_config_id']
    )

    # RPA 실행
    rpa_result = await submit_with_hybrid_config(
        campaign_data=campaign,      # 폼 설정
        site_config=site_config,     # 로그인 설정
        submission_data=submission_data,
        credentials=credentials
    )
```

---

## 🎯 장점

### 1. **로그인 재사용** ✅
```
서울시 에코마일리지 로그인 설정 (rpa_site_configs.id=1)
├── Campaign 10: 대중교통 이용 (재사용)
├── Campaign 11: 재활용 활동 (재사용)
└── Campaign 12: 에너지 절약 (재사용)
```
→ 로그인 설정 변경 시 1곳만 수정

### 2. **폼 개별 관리** ✅
```
Campaign 10: 대중교통 이용
└── Form: transport_type, usage_date, distance

Campaign 11: 재활용 활동
└── Form: recycle_type, activity_desc, photo
```
→ 각 캠페인마다 다른 폼 필드 지원

### 3. **Self-Healing 적용** ✅
- 로그인 셀렉터: `login_selector_strategies` (공통)
- 폼 셀렉터: `rpa_form_selector_strategies` (Campaign별)

### 4. **확장성** ✅
- 새 사이트: `rpa_site_configs`에 로그인 설정 추가
- 새 캠페인: `campaigns`에 폼 설정 추가
- 코드 변경 불필요

---

## 📊 데이터 예시

### 시나리오: 서울시 에코마일리지 2개 캠페인

#### RPA Site Config (공통)
```json
{
  "id": 1,
  "site_code": "seoul_ecomileage",
  "site_name": "서울시 에코마일리지",
  "login_url": "https://ecomileage.seoul.go.kr/login",
  "login_config": {
    "selectors": {
      "username_input": "#username",
      "password_input": "#password",
      "submit_button": "button[type='submit']"
    }
  }
}
```

#### Campaign 1: 대중교통 이용
```json
{
  "id": 10,
  "title": "서울시 에코마일리지 - 대중교통 이용",
  "rpa_site_config_id": 1,  // ← 공통 로그인
  "rpa_form_url": "https://ecomileage.seoul.go.kr/apply/transit",
  "rpa_form_config": {
    "selectors": {
      "transport_type": "#transport_type",
      "usage_date": "#usage_date",
      "submit_button": "#submit-button"
    }
  },
  "rpa_field_mapping": {
    "user_transport": "transport_type",
    "user_date": "usage_date"
  }
}
```

#### Campaign 2: 재활용 활동
```json
{
  "id": 11,
  "title": "서울시 에코마일리지 - 재활용 활동",
  "rpa_site_config_id": 1,  // ← 공통 로그인 (재사용!)
  "rpa_form_url": "https://ecomileage.seoul.go.kr/apply/recycle",
  "rpa_form_config": {
    "selectors": {
      "recycle_type": "#recycle_type",
      "activity_desc": "textarea[name='desc']",
      "photo_upload": "input[type='file']",
      "submit_button": "#submit-button"
    }
  },
  "rpa_field_mapping": {
    "user_recycle": "recycle_type",
    "user_description": "activity_desc",
    "user_photo": "photo_upload"
  }
}
```

---

## 🔧 마이그레이션

### 적용된 마이그레이션

1. **Rollback**: [004_rollback_rpa_site_configs.sql](../database/migrations/004_rollback_rpa_site_configs.sql)
   - 기존 구조 제거

2. **New Structure**: [005_create_hybrid_rpa_structure.sql](../database/migrations/005_create_hybrid_rpa_structure.sql)
   - `rpa_site_configs` 테이블 생성 (로그인만)
   - `campaigns` 테이블에 RPA 폼 컬럼 추가

---

## 🧪 테스트 시나리오

### 1. 로그인 재사용 테스트

```python
# 서울시 에코마일리지 사이트 설정 생성
site_config = await rpa_config_repo.create_config({
    "site_code": "seoul_ecomileage",
    "login_url": "https://ecomileage.seoul.go.kr/login",
    "login_config": {"selectors": {...}}
})

# Campaign 1 생성 (대중교통)
campaign_1 = await campaign_repo.create({
    "title": "대중교통 이용",
    "rpa_site_config_id": site_config['id'],  # 재사용
    "rpa_form_config": {"selectors": {"transport_type": "#type", ...}}
})

# Campaign 2 생성 (재활용)
campaign_2 = await campaign_repo.create({
    "title": "재활용 활동",
    "rpa_site_config_id": site_config['id'],  # 재사용!
    "rpa_form_config": {"selectors": {"recycle_type": "#recycle", ...}}
})

# 두 캠페인 모두 같은 로그인 설정 사용
```

### 2. Self-Healing 테스트

```python
# 로그인 셀렉터가 변경된 경우
site_config['login_selector_strategies'] = {
    "username_input": [
        {"selector": "#username", "priority": 1},      # 기본
        {"selector": "#new_username", "priority": 2},  # 새 셀렉터 추가
        {"selector": "input[name='user']", "priority": 3}
    ]
}

# 첫 번째 전략이 실패하면 자동으로 두 번째 시도
# 모든 Campaign이 자동으로 혜택 받음 (공통 설정이므로)
```

---

## 🚀 향후 확장

### 1. Mission Template 레벨 RPA 지원 (선택사항)

만약 한 Campaign 내에서 Mission마다 다른 폼이 필요하면:

```sql
ALTER TABLE mission_templates
ADD COLUMN rpa_form_config JSONB,
ADD COLUMN rpa_field_mapping JSONB;
```

**우선순위**:
1. `mission_templates.rpa_form_config` (최우선)
2. `campaigns.rpa_form_config` (대체)

### 2. 다국어 지원

```json
{
  "login_config": {
    "selectors": {
      "username_input": {
        "ko": "#username",
        "en": "#user_email"
      }
    }
  }
}
```

---

## 📝 마이그레이션 히스토리

| 날짜 | 마이그레이션 | 설명 |
|------|-------------|------|
| 2025-01-09 | [004_create_rpa_site_configs.sql](../database/migrations/004_create_rpa_site_configs.sql) | 초기 RPA 구조 (mission_templates에 FK) |
| 2025-01-10 | [004_rollback_rpa_site_configs.sql](../database/migrations/004_rollback_rpa_site_configs.sql) | 롤백 (하이브리드로 재설계) |
| 2025-01-10 | [005_create_hybrid_rpa_structure.sql](../database/migrations/005_create_hybrid_rpa_structure.sql) | 하이브리드 구조 (로그인 공유 + 폼 개별) |

---

## ✅ 체크리스트

- [x] DB 마이그레이션 적용
- [x] `rpa_site_configs` 테이블 생성 (로그인만)
- [x] `campaigns` 테이블에 RPA 폼 컬럼 추가
- [x] `SelfHealingAdapter` 하이브리드 구조로 수정
- [x] `submit_with_hybrid_config()` 함수 생성
- [x] `CampaignAgentService` 업데이트
- [x] 스키마 업데이트 (`CampaignResponse`, `RPAConfigBase`)
- [x] 문서화 완료

---

**구현 상태**: ✅ 완료 및 프로덕션 준비 완료
