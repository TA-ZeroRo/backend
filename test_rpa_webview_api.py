"""
RPA WebView API 테스트 스크립트

사용법:
1. Backend 서버가 실행 중이어야 합니다
2. python test_rpa_webview_api.py
"""
import requests
import json

BASE_URL = "http://localhost:8000/api/v1"

def test_generate_script():
    """JavaScript 생성 API 테스트"""
    print("\n" + "="*70)
    print("TEST 1: JavaScript 생성 API")
    print("="*70)

    url = f"{BASE_URL}/rpa-webview/generate-script"
    payload = {
        "campaign_id": 1,
        "mission_template_id": 1,
        "user_id": "test-user-123"
    }

    print(f"\n📤 Request: POST {url}")
    print(f"📋 Payload: {json.dumps(payload, indent=2, ensure_ascii=False)}")

    try:
        response = requests.post(url, json=payload)
        print(f"\n✅ Status Code: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            print(f"\n✨ Response:")
            print(f"  - success: {data.get('success')}")
            print(f"  - field_mapping: {json.dumps(data.get('field_mapping'), indent=4, ensure_ascii=False)}")
            print(f"\n📜 Generated JavaScript (first 500 chars):")
            js_code = data.get('javascript_code', '')
            print(js_code[:500] + "..." if len(js_code) > 500 else js_code)
            return True
        else:
            print(f"\n❌ Error: {response.text}")
            return False

    except Exception as e:
        print(f"\n❌ Exception: {e}")
        return False


def test_get_login_detector():
    """로그인 감지 설정 조회 테스트"""
    print("\n" + "="*70)
    print("TEST 2: 로그인 감지 설정 조회 API")
    print("="*70)

    campaign_id = 1
    url = f"{BASE_URL}/rpa-webview/login-detector/{campaign_id}"

    print(f"\n📤 Request: GET {url}")

    try:
        response = requests.get(url)
        print(f"\n✅ Status Code: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            print(f"\n✨ Response:")
            print(json.dumps(data, indent=2, ensure_ascii=False))
            return True
        else:
            print(f"\n❌ Error: {response.text}")
            return False

    except Exception as e:
        print(f"\n❌ Exception: {e}")
        return False


def test_get_rpa_config():
    """RPA 설정 조회 테스트"""
    print("\n" + "="*70)
    print("TEST 3: RPA 설정 조회 API")
    print("="*70)

    campaign_id = 1
    url = f"{BASE_URL}/rpa-webview/campaigns/{campaign_id}/config"

    print(f"\n📤 Request: GET {url}")

    try:
        response = requests.get(url)
        print(f"\n✅ Status Code: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            print(f"\n✨ Response:")
            print(json.dumps(data, indent=2, ensure_ascii=False))
            return True
        else:
            print(f"\n❌ Error: {response.text}")
            return False

    except Exception as e:
        print(f"\n❌ Exception: {e}")
        return False


def test_report_failure():
    """셀렉터 실패 보고 테스트"""
    print("\n" + "="*70)
    print("TEST 4: 셀렉터 실패 보고 API")
    print("="*70)

    url = f"{BASE_URL}/rpa-webview/report-failure"
    payload = {
        "campaign_id": 1,
        "element_key": "title_field",
        "failed_strategies": [
            {"selector": "input[placeholder='제목']", "priority": 10},
            {"selector": "input[name='title']", "priority": 20}
        ],
        "user_agent": "Mozilla/5.0 (Test)"
    }

    print(f"\n📤 Request: POST {url}")
    print(f"📋 Payload: {json.dumps(payload, indent=2, ensure_ascii=False)}")

    try:
        response = requests.post(url, json=payload)
        print(f"\n✅ Status Code: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            print(f"\n✨ Response:")
            print(json.dumps(data, indent=2, ensure_ascii=False))
            return True
        else:
            print(f"\n❌ Error: {response.text}")
            return False

    except Exception as e:
        print(f"\n❌ Exception: {e}")
        return False


if __name__ == "__main__":
    print("\n🚀 RPA WebView API 테스트 시작")
    print("📍 Base URL:", BASE_URL)

    results = []

    # 각 테스트 실행
    results.append(("JavaScript 생성", test_generate_script()))
    results.append(("로그인 감지 설정", test_get_login_detector()))
    results.append(("RPA 설정 조회", test_get_rpa_config()))
    results.append(("셀렉터 실패 보고", test_report_failure()))

    # 결과 요약
    print("\n" + "="*70)
    print("📊 테스트 결과 요약")
    print("="*70)

    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {name}")

    passed = sum(1 for _, r in results if r)
    total = len(results)
    print(f"\n총 {passed}/{total} 테스트 통과")

    if passed == total:
        print("\n🎉 모든 테스트가 성공했습니다!")
    else:
        print(f"\n⚠️  {total - passed}개 테스트가 실패했습니다.")
