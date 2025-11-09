"""
Test script for ZeroSeoul RPA mission submission
Campaign ID: 3 (탄탄대로 챌린지)
"""
import asyncio
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.services.rpa_core import submit_with_hybrid_config


async def test_zeroseoul_mission_submission():
    """Test RPA submission for ZeroSeoul mission"""

    # Site config (from rpa_site_configs table, id=3)
    site_config = {
        "site_code": "zeroseoul",
        "site_name": "서울시 제로서울",
        "base_url": "https://event.seoul.go.kr",
        "login_url": "https://event.seoul.go.kr/zeroseoul/login",
        "login_config": {
            "selectors": {
                "username_input": "[placeholder*='아이디']",
                "password_input": "input[type='password']",
                "submit_button": "button[type='submit']"
            }
        },
        "login_selector_strategies": {
            "username_input": [
                {"selector": "[placeholder*='아이디']", "priority": 1},
                {"selector": "input[type='text']", "priority": 2},
                {"selector": ".login-text", "priority": 3}
            ],
            "password_input": [
                {"selector": "input[type='password']", "priority": 1},
                {"selector": ".login-text", "priority": 2}
            ],
            "submit_button": [
                {"selector": "button[type='submit']", "priority": 1},
                {"selector": ".btn-ok", "priority": 2}
            ]
        }
    }

    # Campaign config (from campaigns table, id=3)
    campaign_data = {
        "rpa_form_url": "https://event.seoul.go.kr/zeroseoul/",
        "rpa_modal_trigger": "a[href='/zeroseoul/']:has-text('미션인증하기')",  # Modal trigger button
        "rpa_form_config": {
            "selectors": {
                "title_input": "input[placeholder='제목을 입력하세요']",
                "photo_upload": "input[type='file']",
                "content_textarea": "textarea[placeholder='내용을 입력하세요']",
                "submit_button": "button:has-text('등록하기')"
            }
        },
        "rpa_field_mapping": {
            "title": "title_input",
            "photo": "photo_upload",
            "content": "content_textarea"
        },
        "rpa_form_selector_strategies": {
            "title_input": [
                {"selector": "input[placeholder='제목을 입력하세요']", "priority": 1},
                {"selector": ".t-text", "priority": 2}
            ],
            "photo_upload": [
                {"selector": "input[type='file']", "priority": 1}
            ],
            "content_textarea": [
                {"selector": "textarea[placeholder='내용을 입력하세요']", "priority": 1},
                {"selector": ".zero-w", "priority": 2}
            ],
            "submit_button": [
                {"selector": "button:has-text('등록하기')", "priority": 1}
            ]
        }
    }

    # Get absolute path to test image
    test_image_path = Path(__file__).parent / "fixtures" / "mission_photo.jpg"

    # Submission data (미션 인증 내용)
    submission_data = {
        "title": "텀블러 사용 미션 인증",
        "content": "오늘 커피숍에서 일회용컵 대신 텀블러를 사용했습니다. 작은 실천이지만 환경을 위한 좋은 습관을 만들어가고 있습니다!",
        "photo": str(test_image_path.absolute())
    }

    # Login credentials
    credentials = {
        "username": "cjh030808",
        "password": "@m1718m172"
    }

    print("=" * 60)
    print("ZeroSeoul RPA Mission Submission Test")
    print("=" * 60)
    print(f"Site: {site_config['site_name']}")
    print(f"Campaign: 탄탄대로 챌린지")
    print(f"Mission: {submission_data['title']}")
    print("=" * 60)
    print()

    # Execute RPA
    print("Starting RPA automation...")
    result = await submit_with_hybrid_config(
        campaign_data=campaign_data,
        site_config=site_config,
        submission_data=submission_data,
        credentials=credentials
    )

    print()
    print("=" * 60)
    print("RESULT:")
    print("=" * 60)

    if result.get("success"):
        print("✅ SUCCESS!")
        print(f"Message: {result.get('message', 'Mission submitted successfully')}")
    else:
        print("❌ FAILED!")
        print(f"Error: {result.get('error', 'Unknown error')}")

    print("=" * 60)

    return result


if __name__ == "__main__":
    # Run the test
    result = asyncio.run(test_zeroseoul_mission_submission())

    # Exit with appropriate code
    sys.exit(0 if result.get("success") else 1)
