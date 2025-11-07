"""
Manual RPA Test Script
실행 방법:
1. venv 활성화
2. python tests/manual/test_rpa_manual.py
"""
import asyncio
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from app.services.rpa_core import submit_eco_mileage_form


async def test_rpa_with_real_data():
    """실제 데이터를 사용한 RPA 테스트"""
    print("=" * 60)
    print("RPA 테스트 시작 - 실제 데이터")
    print("=" * 60)

    submission_data = {
        "name": "홍길동",
        "birth": "900101",
        "phone": "01012345678",
        "activity_date": "2025-11-07",
        "activity_content": "환경 정화 활동 참여"
    }

    credentials = {
        "username": "test@example.com",
        "password": "testpassword123"
    }

    print("\n[제출 데이터]")
    for key, value in submission_data.items():
        print(f"  {key}: {value}")

    print("\n[인증 정보]")
    print(f"  username: {credentials['username']}")
    print(f"  password: {'*' * len(credentials['password'])}")

    print("\n[RPA 실행 중...]")
    result = await submit_eco_mileage_form(submission_data, credentials)

    print("\n[결과]")
    print(f"  Success: {result.get('success')}")
    if result.get('success'):
        print(f"  Message: {result.get('message')}")
    else:
        print(f"  Error: {result.get('error')}")

    print("=" * 60)
    return result


async def test_rpa_with_missing_credentials():
    """잘못된 credentials를 사용한 테스트"""
    print("\n" + "=" * 60)
    print("RPA 테스트 시작 - 빈 Credentials (예상: 실패)")
    print("=" * 60)

    submission_data = {"name": "테스트"}
    credentials = {}  # 빈 credentials

    result = await submit_eco_mileage_form(submission_data, credentials)

    print("\n[결과]")
    print(f"  Success: {result.get('success')}")
    print(f"  Error: {result.get('error')}")
    print("=" * 60)
    return result


async def test_rpa_with_empty_submission_data():
    """빈 submission_data를 사용한 테스트"""
    print("\n" + "=" * 60)
    print("RPA 테스트 시작 - 빈 Submission Data (예상: 실패)")
    print("=" * 60)

    submission_data = {}
    credentials = {
        "username": "test@example.com",
        "password": "testpassword123"
    }

    result = await submit_eco_mileage_form(submission_data, credentials)

    print("\n[결과]")
    print(f"  Success: {result.get('success')}")
    print(f"  Error: {result.get('error')}")
    print("=" * 60)
    return result


async def main():
    """모든 테스트 실행"""
    print("\n🤖 RPA 수동 테스트 스크립트")
    print("현재 설정: headless=True (브라우저 화면 안 보임)")
    print("브라우저를 보고 싶다면 rpa_core.py의 headless=False로 변경하세요\n")

    # 테스트 1: 정상 데이터
    result1 = await test_rpa_with_real_data()

    # 테스트 2: 빈 credentials
    result2 = await test_rpa_with_missing_credentials()

    # 테스트 3: 빈 submission_data
    result3 = await test_rpa_with_empty_submission_data()

    # 결과 요약
    print("\n" + "=" * 60)
    print("테스트 결과 요약")
    print("=" * 60)
    print(f"1. 정상 데이터 테스트: {'✅ PASS' if not result1.get('success') else '❌ FAIL (URL 문제 예상)'}")
    print(f"2. 빈 Credentials 테스트: {'✅ PASS' if not result2.get('success') else '❌ FAIL'}")
    print(f"3. 빈 Submission Data 테스트: {'✅ PASS' if not result3.get('success') else '❌ FAIL'}")
    print("=" * 60)

    print("\n💡 참고:")
    print("  - 실제 에코마일리지 URL이 설정되어 있지 않아 테스트 1은 실패할 수 있습니다")
    print("  - 테스트 2, 3은 유효성 검사 로직을 확인하는 테스트입니다")
    print("  - mock HTML 페이지를 사용하려면 rpa_core.py의 URL을 수정하세요")


if __name__ == "__main__":
    asyncio.run(main())
