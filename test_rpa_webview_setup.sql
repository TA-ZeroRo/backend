-- RPA WebView 테스트를 위한 Campaign 데이터 업데이트 (DB 구조 완전 활용)
-- 기존 Campaign 중 하나를 선택하여 RPA 정보 추가

-- 예시: Campaign ID 1번을 제로서울 RPA 캠페인으로 설정
UPDATE campaigns
SET
  -- WebView URL
  rpa_form_url = 'https://event.seoul.go.kr/zeroseoul/',

  -- 폼 필드 셀렉터 (한글 필드명 사용)
  rpa_form_config = '{
    "제목 입력란": "input[placeholder*=\"제목\"]",
    "컨텐츠 작성란": "textarea[placeholder*=\"내용\"]",
    "사진 업로드": "input[type=\"file\"]",
    "제출 버튼": "button:contains(\"등록하기\")"
  }'::jsonb,

  -- 실제 입력할 데이터 (우선순위: 여기 데이터 > mission_template)
  rpa_field_mapping = '{
    "제목": "제로서울 테스트 미션",
    "컨텐츠": "제로서울 캠페인 참여 인증입니다. 환경 보호에 동참합니다!",
    "사진": "미션 인증 사진 (WebView에서 직접 업로드)"
  }'::jsonb,

  -- Self-Healing용 예비 셀렉터 (우선순위 낮은 순서)
  rpa_form_selector_strategies = '{
    "제목 입력란": [
      {"selector": "input[name=\"title\"]", "priority": 20},
      {"selector": "#title", "priority": 30}
    ],
    "컨텐츠 작성란": [
      {"selector": "textarea[name=\"content\"]", "priority": 20},
      {"selector": "#content", "priority": 30}
    ],
    "사진 업로드": [
      {"selector": "input[name=\"photo\"]", "priority": 20},
      {"selector": "input[accept*=\"image\"]", "priority": 30}
    ],
    "제출 버튼": [
      {"selector": "button[type=\"submit\"]", "priority": 20},
      {"selector": "input[type=\"submit\"]", "priority": 30}
    ]
  }'::jsonb,

  -- WebView 설정 (로그인 감지 등)
  webview_config = '{
    "login_url": "https://event.seoul.go.kr/zeroseoul/",
    "login_success_indicators": [
      {"type": "url_not_contains", "value": "/login"},
      {"type": "url_contains", "value": "/zeroseoul/"}
    ]
  }'::jsonb

WHERE id = 1;

-- 확인 쿼리
SELECT
  id,
  title,
  rpa_form_url,
  rpa_form_config,
  rpa_field_mapping,
  rpa_form_selector_strategies
FROM campaigns
WHERE rpa_form_url IS NOT NULL;
