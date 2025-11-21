-- Seed: Initial RPA Site Configurations
-- Description: Mock 서울시 에코마일리지 RPA 설정 (테스트용)
-- Created: 2025-01-09

-- ===== Seoul Ecomileage Mock Configuration =====
INSERT INTO rpa_site_configs (
  site_code,
  site_name,
  base_url,
  login_url,
  form_url,
  login_config,
  form_config,
  selector_strategies,
  field_mapping,
  is_active
) VALUES (
  'seoul_ecomileage_mock',
  '서울시 에코마일리지 (테스트용)',
  'file:///C:/Users/goodj/Desktop/TA-ZeroRo/backend/tests/fixtures/mock_eco_form.html',
  'file:///C:/Users/goodj/Desktop/TA-ZeroRo/backend/tests/fixtures/mock_eco_form.html',
  NULL,  -- 로그인 후 자동으로 폼 표시

  -- login_config: 로그인 셀렉터 설정
  '{
    "selectors": {
      "username_input": "#username",
      "password_input": "#password",
      "submit_button": "button[type=\"submit\"]",
      "error_message": ".login-error"
    }
  }'::jsonb,

  -- form_config: 폼 셀렉터 설정
  '{
    "selectors": {
      "name_input": "input[name=\"name\"]",
      "birth_input": "#birth",
      "phone_input": "input[name=\"phone\"]",
      "activity_date_input": "#activity_date",
      "activity_content_textarea": "textarea[name=\"activity_content\"]",
      "submit_button": "#submit-button",
      "success_message": ".success-message",
      "error_message": ".form-error"
    }
  }'::jsonb,

  -- selector_strategies: Self-Healing 전략 (우선순위 기반)
  '{
    "username_input": [
      {"selector": "#username", "priority": 1, "method": "id"},
      {"selector": "input[name=\"username\"]", "priority": 2, "method": "name"},
      {"selector": ".login-form input[type=\"text\"]:first-child", "priority": 3, "method": "class"}
    ],
    "password_input": [
      {"selector": "#password", "priority": 1, "method": "id"},
      {"selector": "input[name=\"password\"]", "priority": 2, "method": "name"},
      {"selector": "input[type=\"password\"]", "priority": 3, "method": "type"}
    ],
    "submit_button": [
      {"selector": "#submit-button", "priority": 1, "method": "id"},
      {"selector": "button[type=\"submit\"]", "priority": 2, "method": "type"},
      {"selector": ".btn-submit", "priority": 3, "method": "class"}
    ],
    "name_input": [
      {"selector": "input[name=\"name\"]", "priority": 1, "method": "name"},
      {"selector": "#name", "priority": 2, "method": "id"}
    ],
    "phone_input": [
      {"selector": "input[name=\"phone\"]", "priority": 1, "method": "name"},
      {"selector": "#phone", "priority": 2, "method": "id"},
      {"selector": "input[type=\"tel\"]", "priority": 3, "method": "type"}
    ]
  }'::jsonb,

  -- field_mapping: submission_data 키 → 폼 셀렉터 매핑
  '{
    "user_name": "name_input",
    "user_birth": "birth_input",
    "user_phone": "phone_input",
    "activity_date": "activity_date_input",
    "description": "activity_content_textarea"
  }'::jsonb,

  true  -- is_active
)
ON CONFLICT (site_code) DO UPDATE SET
  site_name = EXCLUDED.site_name,
  base_url = EXCLUDED.base_url,
  login_url = EXCLUDED.login_url,
  form_url = EXCLUDED.form_url,
  login_config = EXCLUDED.login_config,
  form_config = EXCLUDED.form_config,
  selector_strategies = EXCLUDED.selector_strategies,
  field_mapping = EXCLUDED.field_mapping,
  is_active = EXCLUDED.is_active,
  updated_at = NOW();

-- ===== 확인 =====
SELECT
  id,
  site_code,
  site_name,
  is_active,
  created_at
FROM rpa_site_configs
WHERE site_code = 'seoul_ecomileage_mock';
