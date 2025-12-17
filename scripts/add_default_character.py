"""
기존 사용자들에게 포인트 기준으로 캐릭터 자동 해금 스크립트

모든 사용자를 검사하여 포인트 기준으로 해금 가능하지만 아직 해금되지 않은 캐릭터를 자동으로 추가합니다.

해금 기준:
- 0 포인트 이상: earth_zeroro
- 300 포인트 이상: earth_zeroro + dust_zeroro

예시:
- 이미 earth_zeroro만 있고 350점인 사용자 → dust_zeroro 추가
- characters가 비어있고 150점인 사용자 → earth_zeroro 추가
- characters가 비어있고 400점인 사용자 → earth_zeroro + dust_zeroro 추가
"""
import os
import sys
import asyncio
from pathlib import Path

# 프로젝트 루트를 sys.path에 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from supabase import create_client, Client
from app.core.config import get_supabase_config
from app.config.characters import get_unlockable_characters


async def add_default_character_to_users():
    """모든 사용자에게 포인트 기준으로 캐릭터 자동 해금"""
    try:
        # Supabase 클라이언트 초기화
        url, key = get_supabase_config()
        supabase: Client = create_client(url, key)

        print("🔍 모든 사용자의 캐릭터 해금 상태 확인 중...")

        # 모든 사용자 조회 (total_points도 함께)
        response = supabase.table("profiles").select("id, username, characters, total_points").execute()

        if not response.data:
            print("✅ 사용자가 없습니다.")
            return

        users_to_update = []
        for user in response.data:
            characters = user.get("characters", [])
            total_points = user.get("total_points", 0)

            # 포인트 기준으로 해금 가능한 캐릭터 조회
            unlockable_characters = get_unlockable_characters(total_points)
            if not unlockable_characters:
                unlockable_characters = ["earth_zeroro"]  # 최소한 기본 캐릭터는 있어야 함

            # 현재 보유한 캐릭터 (None이면 빈 배열로 처리)
            current_characters = characters if characters else []

            # 해금 가능하지만 아직 없는 캐릭터 찾기
            missing_characters = [char for char in unlockable_characters if char not in current_characters]

            # 추가할 캐릭터가 있으면 업데이트 대상에 추가
            if missing_characters:
                user["missing_characters"] = missing_characters
                user["unlockable_characters"] = unlockable_characters
                users_to_update.append(user)

        if not users_to_update:
            print("✅ 업데이트가 필요한 사용자가 없습니다. 모든 사용자가 포인트에 맞는 캐릭터를 보유하고 있습니다.")
            return

        print(f"📝 {len(users_to_update)}명의 사용자에게 포인트 기준으로 캐릭터를 추가합니다...")
        print()

        # 각 사용자에게 포인트에 맞는 캐릭터 추가
        success_count = 0
        fail_count = 0
        dust_zeroro_unlocked_count = 0

        for user in users_to_update:
            try:
                user_id = user["id"]
                username = user.get("username", "Unknown")
                total_points = user.get("total_points", 0)
                missing_characters = user["missing_characters"]
                unlockable_characters = user["unlockable_characters"]

                # 캐릭터 업데이트 (전체 해금 가능한 캐릭터 목록으로)
                update_response = supabase.table("profiles").update({
                    "characters": unlockable_characters
                }).eq("id", user_id).execute()

                if update_response.data:
                    missing_names = ", ".join(missing_characters)
                    all_names = ", ".join(unlockable_characters)
                    print(f"  ✅ {username} (ID: {user_id[:8]}..., {total_points}점)")
                    print(f"      추가된 캐릭터: {missing_names}")
                    print(f"      현재 보유 캐릭터: {all_names}")
                    success_count += 1

                    # dust_zeroro가 새로 추가된 경우 카운트
                    if "dust_zeroro" in missing_characters:
                        dust_zeroro_unlocked_count += 1
                else:
                    print(f"  ❌ {username} (ID: {user_id[:8]}...) - 업데이트 실패")
                    fail_count += 1

            except Exception as e:
                print(f"  ❌ {username} (ID: {user_id[:8]}...) - 에러: {str(e)}")
                fail_count += 1

        print("\n" + "="*60)
        print(f"✅ 업데이트 완료: {success_count}명")
        print(f"   - dust_zeroro 새로 해금: {dust_zeroro_unlocked_count}명 (300점 이상)")
        if fail_count > 0:
            print(f"❌ 실패: {fail_count}명")
        print("="*60)

    except Exception as e:
        print(f"❌ 스크립트 실행 중 에러 발생: {str(e)}")
        raise


if __name__ == "__main__":
    print("=" * 60)
    print("기본 캐릭터 추가 스크립트")
    print("=" * 60)
    asyncio.run(add_default_character_to_users())
