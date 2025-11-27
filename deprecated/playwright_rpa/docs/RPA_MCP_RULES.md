# RPA MCP 자동화 규칙 (Rules)

## 📜 개요

이 문서는 Playwright MCP와 Supabase MCP를 사용한 RPA 설정 자동화 시 따라야 할 규칙과 베스트 프랙티스를 정의합니다.

---

## 🎯 핵심 원칙

### 1. 순차적 실행 (Sequential Execution)
- Playwright 분석 → 데이터 구조화 → Supabase 저장 순서를 **반드시** 지킬 것
- 각 단계가 완료된 후 다음 단계로 진행

### 2. 명시적 확인 (Explicit Verification)
- 각 단계마다 결과를 사용자에게 **명시적으로** 보여줄 것
- INSERT/UPDATE 후 RETURNING 절로 저장된 데이터 확인

### 3. 안전한 데이터 처리 (Safe Data Handling)
- JSON 데이터는 항상 `::jsonb` 캐스팅 사용
- SQL Injection 방지를 위해 파라미터화된 쿼리 사용 (가능한 경우)

### 4. Self-Healing 우선 (Self-Healing First)
- 단일 셀렉터보다 **여러 전략**을 우선적으로 수집
- 최소 2개 이상의 셀렉터 후보 확보

---

## 📋 단계별 규칙

### Phase 1: 사전 준비

#### Rule 1.1: 필수 정보 수집
```
✅ DO:
- 사이트 이름, 사이트 코드, URL 확인
- 테스트 계정 준비
- Campaign ID 확인 (폼 설정용)

❌ DON'T:
- 정보 없이 진행 시작
- 프로덕션 계정으로 테스트
```

#### Rule 1.2: MCP 도구 가용성 확인
```
✅ DO:
- Playwright MCP 브라우저 상태 확인
- Supabase MCP 프로젝트 접근 확인

❌ DON'T:
- 브라우저 시작 없이 navigate 시도
```

---

### Phase 2: Playwright 분석

#### Rule 2.1: 페이지 로드 대기
```
✅ DO:
await page.goto(url)
await page.wait_for_load_state('networkidle')

❌ DON'T:
- 로드 완료 전 스냅샷 캡처
- 타임아웃 설정 없이 대기
```

#### Rule 2.2: 스냅샷 우선 사용
```
✅ DO:
1. browser_snapshot 먼저 사용 (접근성 트리)
2. 필요시 browser_take_screenshot (시각적 확인)

❌ DON'T:
- 스크린샷만으로 셀렉터 추측
- 스냅샷 없이 임의의 셀렉터 작성
```

#### Rule 2.3: 셀렉터 검증
```
✅ DO:
- 찾은 셀렉터로 실제 요소 클릭/입력 테스트
- 여러 개 매칭되면 더 구체적인 셀렉터 사용

❌ DON'T:
- 검증 없이 셀렉터 저장
- element.count() > 1인 셀렉터 사용
```

#### Rule 2.4: Self-Healing 전략 수집
```
✅ DO:
최소 2개 이상의 셀렉터 후보 수집:
- Priority 1: 가장 안정적 (id, name)
- Priority 2: 대체 셀렉터 (class, type)
- Priority 3: 포지션 기반 (:first-child 등)

❌ DON'T:
- 단일 셀렉터만 저장
- 동적 ID/Class만 의존
```

---

### Phase 3: 데이터 구조화

#### Rule 3.1: JSON 구조 준수
```
✅ DO:
{
  "selectors": {
    "username_input": "#username",
    "password_input": "#password"
  }
}

❌ DON'T:
{
  "username": "#username"  // selectors 키 누락
}
```

#### Rule 3.2: 필수 필드 검증
```
로그인 설정 (login_config):
✅ REQUIRED:
  - username_input
  - password_input
  - submit_button

⚠️  OPTIONAL:
  - error_message

폼 설정 (rpa_form_config):
✅ REQUIRED:
  - submit_button
  - success_message OR error_message

⚠️  OPTIONAL:
  - 모든 입력 필드 (Campaign 의존)
```

#### Rule 3.3: Field Mapping 규칙
```
✅ DO:
{
  "user_name": "name_input",  // submission_data 키 → selector 키
  "user_birth": "birth_input"
}

❌ DON'T:
{
  "user_name": "#name"  // CSS 셀렉터 직접 매핑 금지
}
```

---

### Phase 4: Supabase 저장

#### Rule 4.1: INSERT 순서
```
✅ DO:
1. rpa_site_configs INSERT 먼저
2. RETURNING으로 ID 받기
3. campaigns UPDATE에서 받은 ID 사용

❌ DON'T:
- campaigns 먼저 UPDATE
- RETURNING 없이 INSERT
```

#### Rule 4.2: JSONB 캐스팅 필수
```
✅ DO:
'{"key": "value"}'::jsonb

❌ DON'T:
'{"key": "value"}'  // 캐스팅 없음
```

#### Rule 4.3: 이스케이프 처리
```
✅ DO:
'{
  "selectors": {
    "username_input": "#username"
  }
}'::jsonb

OR

'{"selectors": {"username_input": "#username"}}'::jsonb

❌ DON'T:
'{'selectors': {'username_input': '#username'}}'  // 작은따옴표
```

#### Rule 4.4: ON CONFLICT 처리
```
✅ DO:
INSERT ... ON CONFLICT (site_code) DO UPDATE SET ...

❌ DON'T:
- 중복 체크 없이 INSERT
- 에러 발생 시 수동 처리
```

---

## 🔍 검증 규칙

### Rule V.1: 저장 후 즉시 검증
```sql
-- INSERT/UPDATE 후
SELECT
  rsc.id,
  rsc.site_code,
  rsc.site_name,
  c.id as campaign_id,
  c.title
FROM rpa_site_configs rsc
LEFT JOIN campaigns c ON c.rpa_site_config_id = rsc.id
WHERE rsc.site_code = 'seoul_ecomileage';
```

### Rule V.2: JSON 구조 검증
```sql
-- login_config에 필수 키 존재 확인
SELECT
  site_code,
  login_config->'selectors'->>'username_input' as username_selector,
  login_config->'selectors'->>'password_input' as password_selector,
  login_config->'selectors'->>'submit_button' as submit_selector
FROM rpa_site_configs
WHERE site_code = 'seoul_ecomileage';

-- NULL인 필드가 있으면 실패
```

### Rule V.3: Self-Healing 전략 검증
```sql
-- 최소 2개 전략 확인
SELECT
  site_code,
  jsonb_array_length(login_selector_strategies->'username_input') as strategy_count
FROM rpa_site_configs
WHERE site_code = 'seoul_ecomileage';

-- strategy_count >= 2 권장
```

---

## ⚠️ 에러 처리 규칙

### Rule E.1: Playwright 에러
```
✅ DO:
- 타임아웃 발생 시: 페이지 새로고침 후 재시도
- 요소 없음: 더 넓은 범위로 스냅샷 재캡처
- 로그인 실패: credentials 재확인

❌ DON'T:
- 에러 무시하고 진행
- 임의의 셀렉터로 대체
```

### Rule E.2: Supabase 에러
```
✅ DO:
- JSON 파싱 에러: 따옴표 이스케이프 확인
- Foreign Key 에러: rpa_site_configs INSERT 먼저
- Unique 제약: ON CONFLICT 사용

❌ DON'T:
- 에러 메시지 무시
- DROP TABLE로 해결 시도
```

### Rule E.3: 롤백 규칙
```
✅ DO:
- INSERT 실패 시 즉시 알림
- 부분 성공 시 완료된 단계 명시
- 재시도 전 데이터 정리

❌ DON'T:
- 중복 데이터 강제 INSERT
- 에러 상태로 진행
```

---

## 🎨 베스트 프랙티스

### BP.1: 셀렉터 우선순위
```
1순위: id (#username)
2순위: name (input[name="username"])
3순위: type (input[type="text"])
4순위: class (.login-input)
5순위: position (:first-child)
```

### BP.2: 네이밍 컨벤션
```
✅ DO:
- site_code: snake_case (seoul_ecomileage)
- selector 키: snake_case + 타입 (username_input, submit_button)

❌ DON'T:
- camelCase (seoulEcomileage)
- 타입 없음 (username, submit)
```

### BP.3: 주석 추가
```sql
INSERT INTO rpa_site_configs (
  site_code,
  site_name,
  -- ... 다른 필드
  login_config
) VALUES (
  'seoul_ecomileage',
  '서울시 에코마일리지',
  -- 2025-01-10 추출, 로그인 셀렉터
  '{...}'::jsonb
);
```

### BP.4: 버전 관리
```json
{
  "login_config": {
    "version": "1.0",
    "extracted_at": "2025-01-10",
    "selectors": {...}
  }
}
```

---

## 📊 체크리스트 템플릿

### 새 사이트 추가 시

```markdown
## [사이트명] RPA 설정

### 1. 정보 수집
- [ ] 사이트 코드: _______________
- [ ] 사이트 이름: _______________
- [ ] 로그인 URL: _______________
- [ ] 테스트 계정: _______________

### 2. 로그인 분석
- [ ] Playwright 페이지 접속 완료
- [ ] 스냅샷 캡처 완료
- [ ] username_input 셀렉터: _______________
- [ ] password_input 셀렉터: _______________
- [ ] submit_button 셀렉터: _______________
- [ ] Self-Healing 전략 2개 이상: [ ]

### 3. 폼 분석
- [ ] 폼 페이지 URL: _______________
- [ ] 모든 필드 셀렉터 확인: [ ]
- [ ] submit_button 셀렉터: _______________
- [ ] success_message 셀렉터: _______________
- [ ] field_mapping 정의 완료: [ ]

### 4. Supabase 저장
- [ ] rpa_site_configs INSERT 완료 (ID: _____)
- [ ] campaigns UPDATE 완료 (Campaign ID: _____)
- [ ] 검증 쿼리 실행 완료: [ ]

### 5. 테스트
- [ ] RPA 실제 실행 성공: [ ]
- [ ] Self-Healing 동작 확인: [ ]
```

---

## 🚨 금지 사항 (Forbidden Actions)

### 절대 하지 말 것

1. **프로덕션 데이터 수정 없이 테스트**
   - 테스트는 항상 테스트 계정으로
   - 프로덕션 Campaign 수정 전 백업

2. **검증 없이 저장**
   - INSERT/UPDATE 후 반드시 SELECT로 확인
   - JSON 구조 유효성 검증

3. **하드코딩**
   - Campaign ID를 코드에 하드코딩 금지
   - 사용자에게 입력 받거나 쿼리로 확인

4. **에러 무시**
   - Playwright 타임아웃 발생 시 즉시 중단
   - SQL 에러 발생 시 롤백 및 재시도

5. **셀렉터 추측**
   - 스냅샷 없이 셀렉터 작성 금지
   - 검증 없이 DB 저장 금지

---

## 📖 관련 문서

- [RPA_MCP_WORKFLOW.md](./RPA_MCP_WORKFLOW.md) - 단계별 워크플로우
- [HYBRID_RPA_STRUCTURE.md](./HYBRID_RPA_STRUCTURE.md) - 하이브리드 구조 설명
- [RPA_SETUP_GUIDE.md](./RPA_SETUP_GUIDE.md) - 설치 및 테스트 가이드

---

**문서 버전**: 1.0
**최종 업데이트**: 2025-01-10
**규칙 준수 필수**: ✅
