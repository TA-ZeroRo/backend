# RPA MCP 빠른 참조 가이드 (Quick Reference)

## 🚀 5분 만에 RPA 설정하기

### 1단계: 로그인 페이지 분석 (2분)

```bash
# 사용자 요청
"[사이트 URL]로 이동해서 로그인 폼의 CSS 셀렉터를 찾아줘"

# Claude 실행
→ browser_navigate(url)
→ browser_snapshot()
→ 셀렉터 추출 및 표시
```

**결과 확인**:
- username_input: `#username`
- password_input: `#password`
- submit_button: `button[type='submit']`

---

### 2단계: 폼 페이지 분석 (2분)

```bash
# 사용자 요청
"테스트 계정으로 로그인하고 [폼 URL]로 이동해서 모든 입력 필드의 셀렉터를 찾아줘"

# Claude 실행
→ browser_type(username)
→ browser_type(password)
→ browser_click(submit)
→ browser_navigate(form_url)
→ browser_snapshot()
→ 모든 필드 셀렉터 추출
```

**결과 확인**:
- 모든 입력 필드 셀렉터
- submit_button
- success_message / error_message

---

### 3단계: DB에 저장 (1분)

```bash
# 사용자 요청
"찾은 셀렉터를 Supabase에 저장해줘.
로그인 설정은 site_code='[사이트코드]'로,
폼 설정은 campaign_id=[번호]에 저장"

# Claude 실행
→ execute_sql(INSERT INTO rpa_site_configs)
→ execute_sql(UPDATE campaigns)
→ 저장 완료 확인
```

**완료!** 🎉

---

## 📝 MCP 함수 치트시트

### Playwright MCP

| 함수 | 용도 | 예시 |
|------|------|------|
| `browser_navigate` | 페이지 이동 | `url: "https://example.com"` |
| `browser_snapshot` | 접근성 트리 캡처 | 셀렉터 자동 추출 |
| `browser_click` | 요소 클릭 | `element: "로그인 버튼", ref: "button[type='submit']"` |
| `browser_type` | 텍스트 입력 | `element: "username", ref: "#username", text: "user"` |
| `browser_take_screenshot` | 스크린샷 | 시각적 확인용 |
| `browser_wait_for` | 대기 | `time: 3` (3초) |

### Supabase MCP

| 함수 | 용도 | 예시 |
|------|------|------|
| `list_projects` | 프로젝트 목록 | ID 확인 |
| `execute_sql` | SQL 실행 | INSERT/UPDATE/SELECT |
| `list_tables` | 테이블 목록 | 스키마 확인 |

---

## 💬 자주 사용하는 요청 문구

### 로그인 분석
```
"https://ecomileage.seoul.go.kr/login 로그인 페이지로 이동해서
username, password, 로그인 버튼의 CSS 셀렉터를 찾아줘.
Self-Healing을 위해 각 요소마다 2-3개의 셀렉터 후보도 찾아줘"
```

### 로그인 테스트
```
"username에 'test@example.com', password에 'test1234'를 입력하고
로그인 버튼을 클릭해줘"
```

### 폼 분석
```
"https://ecomileage.seoul.go.kr/apply 페이지로 이동해서
모든 입력 필드와 제출 버튼의 CSS 셀렉터를 찾아줘"
```

### DB 저장
```
"찾은 모든 셀렉터를 Supabase에 저장해줘.
- 로그인 설정: rpa_site_configs 테이블에 site_code='seoul_ecomileage'로 INSERT
- 폼 설정: campaigns 테이블 id=10에 UPDATE
- field_mapping도 함께 저장 (user_name → name_input 형식)"
```

### 검증
```
"Supabase에서 site_code='seoul_ecomileage'인 RPA 설정을 조회해서
제대로 저장되었는지 확인해줘"
```

---

## 🎯 필수 데이터 구조

### rpa_site_configs INSERT

```sql
INSERT INTO rpa_site_configs (
  site_code,                    -- REQUIRED: 'seoul_ecomileage'
  site_name,                    -- REQUIRED: '서울시 에코마일리지'
  base_url,                     -- REQUIRED: 'https://ecomileage.seoul.go.kr'
  login_url,                    -- REQUIRED: 'https://...../login'
  login_config,                 -- REQUIRED: JSON (username, password, submit)
  login_selector_strategies,    -- OPTIONAL: Self-Healing 전략
  is_active                     -- OPTIONAL: true (기본값)
) VALUES (...);
```

### campaigns UPDATE

```sql
UPDATE campaigns SET
  rpa_site_config_id = ?,       -- REQUIRED: rpa_site_configs.id
  rpa_form_url = ?,             -- OPTIONAL: 폼 페이지 URL
  rpa_form_config = ?,          -- REQUIRED: JSON (필드 셀렉터들)
  rpa_field_mapping = ?,        -- REQUIRED: JSON (user_name → name_input)
  rpa_form_selector_strategies = ?  -- OPTIONAL: Self-Healing 전략
WHERE id = ?;
```

---

## 🔧 자주 발생하는 문제와 해결

| 문제 | 해결 |
|------|------|
| 요소를 찾을 수 없음 | `"5초 기다린 후 스냅샷 다시 캡처해줘"` |
| 여러 요소가 매칭됨 | 더 구체적인 셀렉터 요청 (예: `.login-form #username`) |
| JSON 파싱 에러 | 이스케이프 확인: `"submit_button": "#btn"` (작은따옴표 X) |
| Foreign Key 에러 | rpa_site_configs INSERT 먼저 확인 |
| 로그인 실패 | 테스트 계정 credential 재확인 |

---

## ✅ 완료 체크리스트

```
[ ] 로그인 페이지 분석 완료
    [ ] username_input 셀렉터
    [ ] password_input 셀렉터
    [ ] submit_button 셀렉터
    [ ] Self-Healing 전략 2개 이상

[ ] 폼 페이지 분석 완료
    [ ] 모든 입력 필드 셀렉터
    [ ] submit_button 셀렉터
    [ ] success_message 셀렉터

[ ] field_mapping 정의 완료
    [ ] submission_data 키 → 셀렉터 키 매핑

[ ] Supabase 저장 완료
    [ ] rpa_site_configs INSERT (RETURNING id 확인)
    [ ] campaigns UPDATE (rpa_site_config_id 설정)

[ ] 검증 완료
    [ ] SQL SELECT로 데이터 확인
    [ ] JSON 구조 유효성 확인
```

---

## 📊 예시: 서울시 에코마일리지

### 완성된 데이터

```sql
-- 1. 로그인 설정 저장
INSERT INTO rpa_site_configs (
  site_code, site_name, base_url, login_url, login_config, login_selector_strategies
) VALUES (
  'seoul_ecomileage',
  '서울시 에코마일리지',
  'https://ecomileage.seoul.go.kr',
  'https://ecomileage.seoul.go.kr/login',
  '{"selectors": {"username_input": "#username", "password_input": "#password", "submit_button": "button[type=\"submit\"]"}}'::jsonb,
  '{"username_input": [{"selector": "#username", "priority": 1}, {"selector": "input[name=\"username\"]", "priority": 2}]}'::jsonb
) RETURNING id;
-- 반환: id = 1

-- 2. 폼 설정 저장
UPDATE campaigns SET
  rpa_site_config_id = 1,
  rpa_form_url = 'https://ecomileage.seoul.go.kr/apply/transit',
  rpa_form_config = '{"selectors": {"name_input": "input[name=\"name\"]", "submit_button": "#submit-button"}}'::jsonb,
  rpa_field_mapping = '{"user_name": "name_input", "user_birth": "birth_input"}'::jsonb
WHERE id = 10
RETURNING id, title;
```

---

## 🚀 고급 팁

### Tip 1: 한 번에 여러 셀렉터 찾기
```
"로그인 페이지에서 다음을 모두 찾아줘:
1. username 입력창 (최소 2개 셀렉터)
2. password 입력창 (최소 2개 셀렉터)
3. 로그인 버튼 (최소 2개 셀렉터)
4. 에러 메시지 영역"
```

### Tip 2: 동적 요소 대응
```
"username 입력창의 id가 동적으로 변하는 것 같아.
name, placeholder, class 기반 셀렉터를 추가로 찾아줘"
```

### Tip 3: iframe 처리
```
"페이지에 iframe이 있나 확인하고,
있으면 각 iframe 내부의 폼 요소도 찾아줘"
```

### Tip 4: 일괄 저장
```
"지금까지 찾은 모든 셀렉터를 정리해서 보여주고,
확인 후 Supabase에 한 번에 저장해줘"
```

---

## 📚 더 알아보기

- **상세 가이드**: [RPA_MCP_WORKFLOW.md](./RPA_MCP_WORKFLOW.md)
- **규칙 문서**: [RPA_MCP_RULES.md](./RPA_MCP_RULES.md)
- **구조 설명**: [HYBRID_RPA_STRUCTURE.md](./HYBRID_RPA_STRUCTURE.md)

---

**최종 업데이트**: 2025-01-10
**예상 소요 시간**: 5-10분 (사이트당)
