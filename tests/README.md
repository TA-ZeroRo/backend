# RPA 테스트 가이드

## 🚀 빠른 시작

### 1. Playwright 브라우저 설치

```bash
# venv 활성화 후
python -m playwright install chromium
```

### 2. Mock HTML 페이지 열기

```bash
# 브라우저에서 직접 열기
start tests/fixtures/mock_eco_form.html

# 또는 절대 경로로
C:\Users\goodj\Desktop\TA-ZeroRo\backend\tests\fixtures\mock_eco_form.html
```

테스트 계정:
- **ID**: test@example.com
- **PW**: password123

### 3. RPA 수동 테스트 실행

```bash
python tests/manual/test_rpa_manual.py
```

### 4. Pytest 자동 테스트 실행

```bash
# pytest 설치 (아직 안 했다면)
pip install pytest pytest-asyncio

# 테스트 실행
pytest tests/test_rpa_core.py -v
```

## 🎬 RPA 시각적으로 확인하기

### 방법 1: 환경변수 설정 (추천)

`.env` 파일에 추가:
```bash
RPA_HEADLESS=false
RPA_SLOW_MO=1000
RPA_SCREENSHOTS=true
```

### 방법 2: 코드 직접 수정

`app/services/rpa_core.py` 파일 상단:
```python
HEADLESS_MODE = False  # True → False
SLOW_MO = 1000        # 0 → 1000
ENABLE_SCREENSHOTS = True  # False → True
```

## 🧪 테스트 시나리오

### 시나리오 1: Mock HTML로 로컬 테스트

1. `tests/fixtures/mock_eco_form.html`을 브라우저에서 열기
2. `app/services/rpa_core.py`에서 URL 수정:
   ```python
   login_url = "file:///C:/Users/goodj/Desktop/TA-ZeroRo/backend/tests/fixtures/mock_eco_form.html"
   apply_url = login_url  # 같은 페이지 사용
   ```
3. 환경변수 설정: `RPA_HEADLESS=false`, `RPA_SLOW_MO=1000`
4. 테스트 실행: `python tests/manual/test_rpa_manual.py`

### 시나리오 2: Headless 모드로 자동 테스트

```bash
# 환경변수 기본값 사용 (headless=true)
pytest tests/test_rpa_core.py -v
```

### 시나리오 3: 스크린샷 디버깅

```bash
# .env 파일에 설정
RPA_SCREENSHOTS=true

# 테스트 실행 후 스크린샷 확인
ls logs/screenshots/
```

스크린샷 파일명 규칙:
- `rpa_YYYYMMDD_HHMMSS_01_login_page.png`
- `rpa_YYYYMMDD_HHMMSS_02_before_login.png`
- `rpa_YYYYMMDD_HHMMSS_ERROR_*.png` (에러 발생 시)
- `rpa_YYYYMMDD_HHMMSS_SUCCESS_final.png` (성공 시)

## 📊 테스트 결과 해석

### 예상되는 테스트 결과

| 테스트 | 예상 결과 | 이유 |
|--------|-----------|------|
| test_missing_username | ✅ PASS | credentials 검증 로직 작동 |
| test_empty_submission_data | ✅ PASS | submission_data 검증 로직 작동 |
| test_rpa_with_real_data | ❌ FAIL | 실제 에코마일리지 URL이 없음 (정상) |

### 실제 에코마일리지 사이트 테스트

실제 URL이 있다면 `app/services/rpa_core.py`에서 수정:
```python
login_url = "https://실제도메인.com/login"
apply_url = "https://실제도메인.com/apply"
```

## 🐛 디버깅 팁

### 1. 브라우저가 안 뜨는 경우
```bash
# Chromium 재설치
python -m playwright install --force chromium
```

### 2. 타임아웃 에러
- `app/services/rpa_core.py`에서 timeout 값 증가 (30000 → 60000)
- 네트워크 상태 확인

### 3. Selector가 안 찾아지는 경우
- `RPA_HEADLESS=false`로 설정해서 페이지 구조 확인
- `RPA_SCREENSHOTS=true`로 설정해서 각 단계 스크린샷 확인
- 브라우저 개발자 도구로 실제 selector 확인

### 4. 로그 확인
```bash
# 상세 로그 확인
tail -f logs/zeroro.log
```

## 📝 API 엔드포인트 테스트

Swagger UI에서 테스트:
```
http://127.0.0.1:8000/docs
```

또는 curl:
```bash
curl -X POST "http://127.0.0.1:8000/api/v1/campaign-agent/mission-logs/1" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "123e4567-e89b-12d3-a456-426614174000",
    "submission_data": {
      "name": "홍길동",
      "birth": "900101",
      "phone": "01012345678",
      "activity_date": "2025-11-07",
      "activity_content": "환경 정화 활동"
    },
    "credentials": {
      "username": "test@example.com",
      "password": "password123"
    }
  }'
```

## 🔧 환경변수 전체 목록

| 변수명 | 기본값 | 설명 |
|--------|--------|------|
| RPA_HEADLESS | true | false로 설정하면 브라우저가 화면에 보임 |
| RPA_SLOW_MO | 0 | 각 액션 사이 딜레이 (ms), 디버깅 시 1000 추천 |
| RPA_SCREENSHOTS | false | true로 설정하면 각 단계 스크린샷 저장 |
| LOG_LEVEL | INFO | 로그 레벨 (DEBUG/INFO/WARNING/ERROR) |

## 💡 추가 정보

- Mock HTML 페이지는 완전히 독립적으로 동작합니다 (서버 불필요)
- 실제 폼 제출은 JavaScript로 시뮬레이션됩니다
- 테스트 계정 외 다른 credentials로 로그인하면 에러 메시지가 표시됩니다
