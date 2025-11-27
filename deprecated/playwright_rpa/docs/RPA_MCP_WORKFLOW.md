# RPA 설정 자동화 워크플로우 (MCP 기반)

## 📋 개요

이 문서는 **Playwright MCP**로 웹사이트의 CSS 셀렉터를 자동으로 찾고, **Supabase MCP**로 DB에 저장하는 완전 자동화 워크플로우를 설명합니다.

### 핵심 프로세스

```
1. Playwright MCP로 로그인 페이지 접속 및 분석
   ↓
2. CSS 셀렉터 자동 추출 (username, password, submit)
   ↓
3. Playwright MCP로 폼 페이지 접속 및 분석
   ↓
4. 폼 필드 셀렉터 자동 추출
   ↓
5. 데이터 구조화 (JSON)
   ↓
6. Supabase MCP로 rpa_site_configs 테이블에 INSERT
   ↓
7. Supabase MCP로 campaigns 테이블 UPDATE
```

---

## 🎯 사전 준비

### 필요한 정보 체크리스트

- [ ] 사이트 이름 (예: 서울시 에코마일리지)
- [ ] 사이트 코드 (예: seoul_ecomileage)
- [ ] 로그인 페이지 URL
- [ ] 폼 제출 페이지 URL (선택)
- [ ] 테스트 계정 (username, password)
- [ ] Campaign ID (폼 설정을 연결할 캠페인)

### MCP 도구 확인

```bash
# Playwright MCP 도구 확인
- mcp__microsoft-playwright-mcp__browser_navigate
- mcp__microsoft-playwright-mcp__browser_snapshot
- mcp__microsoft-playwright-mcp__browser_click
- mcp__microsoft-playwright-mcp__browser_type

# Supabase MCP 도구 확인
- mcp__supabase__execute_sql
- mcp__supabase__list_projects
```

---

## 📖 Step-by-Step 가이드

### Step 1: 로그인 페이지 분석 (Playwright MCP)

#### 1-1. 브라우저로 로그인 페이지 접속

**MCP 함수**: `mcp__microsoft-playwright-mcp__browser_navigate`

```
입력 파라미터:
- url: "https://ecomileage.seoul.go.kr/login"

요청 예시:
"서울시 에코마일리지 로그인 페이지(https://ecomileage.seoul.go.kr/login)로 이동해줘"
```

#### 1-2. 페이지 스냅샷 캡처

**MCP 함수**: `mcp__microsoft-playwright-mcp__browser_snapshot`

```
요청 예시:
"현재 페이지의 접근성 스냅샷을 캡처해줘"

반환 예시:
{
  "snapshot": "
    textbox 'Username' [#username]
    textbox 'Password' [#password]
    button 'Login' [type='submit']
    text '.login-error' (에러 메시지 영역)
  "
}
```

#### 1-3. 로그인 셀렉터 추출 및 기록

**추출해야 할 항목**:
- `username_input`: 아이디 입력창 셀렉터
- `password_input`: 비밀번호 입력창 셀렉터
- `submit_button`: 로그인 버튼 셀렉터
- `error_message`: 에러 메시지 영역 셀렉터 (선택)

**JSON 구조로 정리**:
```json
{
  "login_config": {
    "selectors": {
      "username_input": "#username",
      "password_input": "#password",
      "submit_button": "button[type='submit']",
      "error_message": ".login-error"
    }
  }
}
```

#### 1-4. Self-Healing 전략 수립 (선택)

**여러 셀렉터 후보 찾기**:

```
요청 예시:
"username 입력창을 찾을 수 있는 모든 가능한 CSS 셀렉터를 알려줘"

가능한 셀렉터들:
1. #username (id)
2. input[name="username"] (name attribute)
3. input[type="text"]:first-child (type + position)
4. .login-form input[type="text"] (class + type)
```

**Self-Healing 전략 JSON**:
```json
{
  "login_selector_strategies": {
    "username_input": [
      {"selector": "#username", "priority": 1, "method": "id"},
      {"selector": "input[name='username']", "priority": 2, "method": "name"},
      {"selector": "input[type='text']:first-child", "priority": 3, "method": "type"}
    ],
    "password_input": [
      {"selector": "#password", "priority": 1, "method": "id"},
      {"selector": "input[name='password']", "priority": 2, "method": "name"},
      {"selector": "input[type='password']", "priority": 3, "method": "type"}
    ]
  }
}
```

---

### Step 2: 폼 페이지 분석 (Playwright MCP)

#### 2-1. 로그인 실행 (테스트)

**MCP 함수**: `mcp__microsoft-playwright-mcp__browser_type`, `mcp__microsoft-playwright-mcp__browser_click`

```
요청 예시:
1. "username 입력창(#username)에 'testuser@example.com'을 입력해줘"
2. "password 입력창(#password)에 'test1234'를 입력해줘"
3. "로그인 버튼(button[type='submit'])을 클릭해줘"
```

#### 2-2. 폼 페이지로 이동

```
요청 예시:
"https://ecomileage.seoul.go.kr/apply/transit 페이지로 이동해줘"
```

#### 2-3. 폼 스냅샷 캡처

**MCP 함수**: `mcp__microsoft-playwright-mcp__browser_snapshot`

```
반환 예시:
{
  "snapshot": "
    textbox 'Name' [input[name='name']]
    textbox 'Birth Date' [#birth]
    textbox 'Phone' [input[name='phone']]
    combobox 'Transport Type' [#transport_type]
    textbox 'Usage Date' [#usage_date]
    textbox 'Distance' [input[name='distance']]
    button 'Submit' [#submit-button]
    text '.success-message' (성공 메시지)
    text '.form-error' (에러 메시지)
  "
}
```

#### 2-4. 폼 셀렉터 추출 및 기록

**추출해야 할 항목**:
- 모든 입력 필드 셀렉터
- `submit_button`: 제출 버튼 셀렉터
- `success_message`: 성공 메시지 셀렉터
- `error_message`: 에러 메시지 셀렉터

**JSON 구조로 정리**:
```json
{
  "rpa_form_config": {
    "selectors": {
      "name_input": "input[name='name']",
      "birth_input": "#birth",
      "phone_input": "input[name='phone']",
      "transport_type": "#transport_type",
      "usage_date": "#usage_date",
      "distance": "input[name='distance']",
      "submit_button": "#submit-button",
      "success_message": ".success-message",
      "error_message": ".form-error"
    }
  }
}
```

#### 2-5. 필드 매핑 정의

**submission_data 키 → 폼 셀렉터 키 매핑**:

```json
{
  "rpa_field_mapping": {
    "user_name": "name_input",
    "user_birth": "birth_input",
    "user_phone": "phone_input",
    "user_transport": "transport_type",
    "user_date": "usage_date",
    "user_distance": "distance"
  }
}
```

**설명**:
- `user_name`: 사용자가 제출하는 데이터 키
- `name_input`: `rpa_form_config.selectors`에 정의된 셀렉터 키

---

### Step 3: 데이터 구조화

#### 3-1. 로그인 설정 JSON 완성

```json
{
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
    ],
    "password_input": [
      {"selector": "#password", "priority": 1, "method": "id"},
      {"selector": "input[name='password']", "priority": 2, "method": "name"}
    ]
  },
  "is_active": true
}
```

#### 3-2. 폼 설정 JSON 완성

```json
{
  "campaign_id": 10,
  "rpa_form_url": "https://ecomileage.seoul.go.kr/apply/transit",
  "rpa_form_config": {
    "selectors": {
      "name_input": "input[name='name']",
      "birth_input": "#birth",
      "phone_input": "input[name='phone']",
      "transport_type": "#transport_type",
      "usage_date": "#usage_date",
      "distance": "input[name='distance']",
      "submit_button": "#submit-button",
      "success_message": ".success-message",
      "error_message": ".form-error"
    }
  },
  "rpa_field_mapping": {
    "user_name": "name_input",
    "user_birth": "birth_input",
    "user_phone": "phone_input",
    "user_transport": "transport_type",
    "user_date": "usage_date",
    "user_distance": "distance"
  },
  "rpa_form_selector_strategies": {
    "name_input": [
      {"selector": "input[name='name']", "priority": 1, "method": "name"},
      {"selector": "#name", "priority": 2, "method": "id"}
    ]
  }
}
```

---

### Step 4: Supabase에 저장

#### 4-1. Project ID 확인

**MCP 함수**: `mcp__supabase__list_projects`

```
요청 예시:
"Supabase 프로젝트 목록을 보여줘"

반환:
{
  "id": "aldghxocvhbscghaztfk",
  "name": "zeroro"
}
```

#### 4-2. rpa_site_configs 테이블에 INSERT

**MCP 함수**: `mcp__supabase__execute_sql`

```sql
INSERT INTO rpa_site_configs (
  site_code,
  site_name,
  base_url,
  login_url,
  login_config,
  login_selector_strategies,
  is_active
) VALUES (
  'seoul_ecomileage',
  '서울시 에코마일리지',
  'https://ecomileage.seoul.go.kr',
  'https://ecomileage.seoul.go.kr/login',
  '{
    "selectors": {
      "username_input": "#username",
      "password_input": "#password",
      "submit_button": "button[type=\"submit\"]",
      "error_message": ".login-error"
    }
  }'::jsonb,
  '{
    "username_input": [
      {"selector": "#username", "priority": 1, "method": "id"},
      {"selector": "input[name=\"username\"]", "priority": 2, "method": "name"}
    ],
    "password_input": [
      {"selector": "#password", "priority": 1, "method": "id"},
      {"selector": "input[name=\"password\"]", "priority": 2, "method": "name"}
    ]
  }'::jsonb,
  true
)
RETURNING id, site_code, site_name;
```

**요청 예시**:
```
"Supabase 프로젝트 'aldghxocvhbscghaztfk'에 다음 SQL을 실행해줘:
[위의 INSERT 문]"
```

**반환 확인**:
```json
{
  "id": 1,
  "site_code": "seoul_ecomileage",
  "site_name": "서울시 에코마일리지"
}
```

#### 4-3. campaigns 테이블 UPDATE

**MCP 함수**: `mcp__supabase__execute_sql`

```sql
UPDATE campaigns
SET
  rpa_site_config_id = 1,  -- 위에서 받은 ID
  rpa_form_url = 'https://ecomileage.seoul.go.kr/apply/transit',
  rpa_form_config = '{
    "selectors": {
      "name_input": "input[name=\"name\"]",
      "birth_input": "#birth",
      "phone_input": "input[name=\"phone\"]",
      "transport_type": "#transport_type",
      "usage_date": "#usage_date",
      "distance": "input[name=\"distance\"]",
      "submit_button": "#submit-button",
      "success_message": ".success-message",
      "error_message": ".form-error"
    }
  }'::jsonb,
  rpa_field_mapping = '{
    "user_name": "name_input",
    "user_birth": "birth_input",
    "user_phone": "phone_input",
    "user_transport": "transport_type",
    "user_date": "usage_date",
    "user_distance": "distance"
  }'::jsonb,
  rpa_form_selector_strategies = '{
    "name_input": [
      {"selector": "input[name=\"name\"]", "priority": 1, "method": "name"},
      {"selector": "#name", "priority": 2, "method": "id"}
    ]
  }'::jsonb
WHERE id = 10
RETURNING id, title, rpa_site_config_id;
```

**반환 확인**:
```json
{
  "id": 10,
  "title": "서울시 에코마일리지 - 대중교통 이용",
  "rpa_site_config_id": 1
}
```

---

## 🎬 실제 예시: 서울시 에코마일리지 전체 워크플로우

### 시나리오
"서울시 에코마일리지 - 대중교통 이용" 캠페인의 RPA 설정을 처음부터 끝까지 자동화

### 전체 대화 흐름

```
👤 User:
"서울시 에코마일리지 로그인 페이지 https://ecomileage.seoul.go.kr/login 로 이동해줘"

🤖 Claude:
[mcp__microsoft-playwright-mcp__browser_navigate 실행]
✅ 페이지 로드 완료

---

👤 User:
"현재 페이지의 스냅샷을 캡처해서 로그인 폼의 CSS 셀렉터를 찾아줘"

🤖 Claude:
[mcp__microsoft-playwright-mcp__browser_snapshot 실행]

다음 로그인 요소를 찾았습니다:
- Username 입력: #username
- Password 입력: #password
- 로그인 버튼: button[type='submit']
- 에러 메시지: .login-error

추가 셀렉터 후보:
- Username: input[name='username'], input[type='text']:first-child
- Password: input[name='password'], input[type='password']

---

👤 User:
"username에 'test@example.com', password에 'test1234'를 입력하고 로그인 버튼을 클릭해줘"

🤖 Claude:
[mcp__microsoft-playwright-mcp__browser_type × 2]
[mcp__microsoft-playwright-mcp__browser_click]
✅ 로그인 성공

---

👤 User:
"https://ecomileage.seoul.go.kr/apply/transit 페이지로 이동해서 폼 필드의 셀렉터를 찾아줘"

🤖 Claude:
[mcp__microsoft-playwright-mcp__browser_navigate]
[mcp__microsoft-playwright-mcp__browser_snapshot]

다음 폼 필드를 찾았습니다:
- 이름: input[name='name']
- 생년월일: #birth
- 전화번호: input[name='phone']
- 교통수단: #transport_type
- 이용일자: #usage_date
- 거리: input[name='distance']
- 제출 버튼: #submit-button
- 성공 메시지: .success-message
- 에러 메시지: .form-error

---

👤 User:
"이제 찾은 모든 셀렉터 정보를 Supabase에 저장해줘.
로그인 설정은 rpa_site_configs 테이블에,
폼 설정은 campaigns 테이블(id=10)에 저장해줘"

🤖 Claude:
[mcp__supabase__execute_sql - INSERT into rpa_site_configs]
✅ RPA Site Config 저장 완료 (id: 1)

[mcp__supabase__execute_sql - UPDATE campaigns]
✅ Campaign 10번 RPA 폼 설정 업데이트 완료

저장 완료:
- rpa_site_configs.id: 1 (seoul_ecomileage)
- campaigns.id: 10 (rpa_site_config_id: 1)

이제 Campaign 10번은 서울시 에코마일리지 로그인을 사용하여
대중교통 이용 폼을 자동으로 제출할 수 있습니다!
```

---

## 🔧 고급 기능

### 1. Self-Healing 전략 추가

**기존 설정에 새로운 셀렉터 전략 추가**:

```sql
-- username_input에 새 전략 추가
UPDATE rpa_site_configs
SET login_selector_strategies = jsonb_set(
  login_selector_strategies,
  '{username_input}',
  login_selector_strategies->'username_input' ||
  '[{"selector": ".login-form input[type=text]", "priority": 4, "method": "class"}]'::jsonb
)
WHERE site_code = 'seoul_ecomileage';
```

### 2. 여러 Campaign이 같은 로그인 공유

```sql
-- Campaign 11번도 같은 로그인 사용 (재활용 활동)
UPDATE campaigns
SET
  rpa_site_config_id = 1,  -- seoul_ecomileage 로그인 재사용
  rpa_form_url = 'https://ecomileage.seoul.go.kr/apply/recycle',
  rpa_form_config = '{
    "selectors": {
      "recycle_type": "#recycle_type",
      "activity_desc": "textarea[name=\"desc\"]",
      "photo": "input[type=\"file\"]",
      "submit_button": "#submit-button"
    }
  }'::jsonb,
  rpa_field_mapping = '{
    "user_recycle": "recycle_type",
    "user_description": "activity_desc",
    "user_photo": "photo"
  }'::jsonb
WHERE id = 11;
```

### 3. 설정 검증

```sql
-- 저장된 설정 확인
SELECT
  rsc.id,
  rsc.site_code,
  rsc.site_name,
  c.id as campaign_id,
  c.title,
  c.rpa_form_url
FROM rpa_site_configs rsc
LEFT JOIN campaigns c ON c.rpa_site_config_id = rsc.id
WHERE rsc.site_code = 'seoul_ecomileage';
```

---

## ⚠️ 트러블슈팅

### 문제 1: 셀렉터를 찾을 수 없음

**증상**: Playwright 스냅샷에 원하는 요소가 보이지 않음

**해결**:
1. 페이지가 완전히 로드되었는지 확인
   ```
   "페이지 로드 완료를 기다려줘 (networkidle)"
   ```

2. JavaScript로 렌더링되는 경우
   ```
   "5초 기다린 후 다시 스냅샷 캡처해줘"
   ```

3. iframe 내부에 있는 경우
   ```
   "페이지의 모든 iframe을 찾아서 각각 스냅샷 캡처해줘"
   ```

### 문제 2: 로그인 후 리다이렉트

**증상**: 로그인 후 예상치 못한 페이지로 이동

**해결**:
```
"로그인 후 현재 URL을 알려줘"
→ 실제 폼 URL 확인 후 rpa_form_url에 반영
```

### 문제 3: JSON 문법 오류

**증상**: Supabase INSERT 실패 (JSON 파싱 에러)

**해결**:
```sql
-- JSON 이스케이프 주의
-- 잘못된 예: {"selector": "#username"}
-- 올바른 예: {"selector": "#username"}

-- JSONB 캐스팅 필수
'{"key": "value"}'::jsonb
```

### 문제 4: 셀렉터가 여러 개 매칭됨

**증상**: `element.count() > 1`

**해결**:
```json
{
  "selectors": {
    // 더 구체적인 셀렉터 사용
    "username_input": ".login-form input[name='username']",
    // 또는 :first-child 사용
    "username_input": "input[type='text']:first-child"
  }
}
```

### 문제 5: 동적 ID/Class

**증상**: 페이지 새로고침 시 ID가 변경됨 (예: `input-12345`)

**해결**: Self-Healing 전략에 안정적인 셀렉터 추가
```json
{
  "username_input": [
    {"selector": "input[name='username']", "priority": 1, "method": "name"},
    {"selector": "input[placeholder='Username']", "priority": 2, "method": "placeholder"},
    {"selector": ".login-form input[type='text']", "priority": 3, "method": "class"}
  ]
}
```

---

## 📝 체크리스트

### 로그인 설정 완료

- [ ] 로그인 페이지 URL 확인
- [ ] username_input 셀렉터 확인
- [ ] password_input 셀렉터 확인
- [ ] submit_button 셀렉터 확인
- [ ] error_message 셀렉터 확인 (선택)
- [ ] Self-Healing 전략 2개 이상 설정 (권장)
- [ ] 테스트 로그인 성공 확인
- [ ] rpa_site_configs 테이블에 INSERT 완료

### 폼 설정 완료

- [ ] 폼 페이지 URL 확인
- [ ] 모든 입력 필드 셀렉터 확인
- [ ] submit_button 셀렉터 확인
- [ ] success_message 셀렉터 확인
- [ ] error_message 셀렉터 확인
- [ ] field_mapping 정의 완료
- [ ] campaigns 테이블 UPDATE 완료

### 검증

- [ ] SQL 쿼리로 저장된 데이터 확인
- [ ] JSON 구조 유효성 확인
- [ ] RPA 실제 실행 테스트

---

## 🚀 다음 단계

1. **테스트 실행**: [RPA_SETUP_GUIDE.md](./RPA_SETUP_GUIDE.md) 참고
2. **Self-Healing 모니터링**: 로그 확인하여 어떤 전략이 사용되는지 확인
3. **다른 사이트 추가**: 이 워크플로우를 반복하여 추가 사이트 설정

---

**문서 버전**: 1.0
**최종 업데이트**: 2025-01-10
**관련 문서**:
- [HYBRID_RPA_STRUCTURE.md](./HYBRID_RPA_STRUCTURE.md)
- [RPA_SETUP_GUIDE.md](./RPA_SETUP_GUIDE.md)
