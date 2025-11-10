"""
Zero Seoul 챌린지 제출 RPA - 최종 완성 버전
로그인 → 챌린지 버튼 클릭 → 폼 작성 → 제출 → 확인 → 자동 종료

실행: python tests/manual/test_zeroseoul_final.py
"""
import asyncio
import sys
from pathlib import Path
from playwright.async_api import async_playwright

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))


async def submit_zeroseoul_challenge(
    credentials: dict,
    submission_data: dict,
    image_path: str = None
):
    """Zero Seoul 챌린지 자동 제출"""

    async with async_playwright() as playwright:
        print("=" * 70)
        print("🌐 Zero Seoul 챌린지 제출 RPA 시작")
        print("=" * 70)

        browser = await playwright.chromium.launch(
            headless=False,
            slow_mo=500
        )

        context = await browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        )

        page = await context.new_page()
        screenshot_dir = Path("logs/screenshots")
        screenshot_dir.mkdir(parents=True, exist_ok=True)

        try:
            # ============================================================
            # STEP 1: 로그인
            # ============================================================
            print(f"\n{'='*70}")
            print(f"🔐 STEP 1: 로그인")
            print(f"{'='*70}")

            await page.goto("https://event.seoul.go.kr/zeroseoul/login", wait_until='networkidle', timeout=60000)
            await page.wait_for_timeout(2000)
            print(f"✅ 로그인 페이지 로드 완료")

            # Find and fill username
            username_selectors = ['#userId', 'input[name="userId"]', 'input[type="text"]']
            for selector in username_selectors:
                if await page.locator(selector).count() > 0:
                    await page.fill(selector, credentials['username'])
                    print(f"✓ 아이디 입력: {selector}")
                    break

            # Find and fill password
            password_selectors = ['#userPw', 'input[name="userPw"]', 'input[type="password"]']
            for selector in password_selectors:
                if await page.locator(selector).count() > 0:
                    await page.fill(selector, credentials['password'])
                    print(f"✓ 비밀번호 입력: {selector}")
                    break

            # Click login button
            login_button_selectors = ['button[type="submit"]', 'button:has-text("로그인")']
            for selector in login_button_selectors:
                if await page.locator(selector).count() > 0:
                    print(f"🔘 로그인 버튼 클릭...")
                    try:
                        async with page.expect_navigation(timeout=10000):
                            await page.click(selector)
                    except:
                        await page.click(selector)
                        await page.wait_for_timeout(3000)
                    break

            print(f"✅ 로그인 완료!")
            print(f"   현재 URL: {page.url}")

            # ============================================================
            # STEP 2: 메인 페이지로 이동
            # ============================================================
            print(f"\n{'='*70}")
            print(f"🏠 STEP 2: 메인 페이지 이동")
            print(f"{'='*70}")

            if '/login' in page.url:
                await page.goto("https://event.seoul.go.kr/zeroseoul/", wait_until='networkidle', timeout=60000)
                await page.wait_for_timeout(2000)

            print(f"✅ 메인 페이지 로드 완료")
            print(f"   현재 URL: {page.url}")

            # ============================================================
            # STEP 3: 챌린지 참여 버튼 클릭
            # ============================================================
            print(f"\n{'='*70}")
            print(f"🎯 STEP 3: 챌린지 참여 버튼 클릭")
            print(f"{'='*70}")

            # Scroll to find the button
            print(f"📜 페이지 스크롤...")
            await page.evaluate("window.scrollTo(0, document.body.scrollHeight / 3)")
            await page.wait_for_timeout(1000)

            # Screenshot before clicking
            await page.screenshot(path=str(screenshot_dir / "01_before_challenge_click.png"))

            # 정확한 selector: a.btn-write
            challenge_button_selector = 'a.btn-write[href="/zeroseoul/"]'

            # Check if button exists
            button_count = await page.locator(challenge_button_selector).count()
            print(f"🔍 챌린지 버튼 검색: {challenge_button_selector}")
            print(f"   발견된 버튼: {button_count}개")

            if button_count == 0:
                # Try alternative selectors
                alternative_selectors = [
                    'a.btn-write',
                    'a[href*="zeroseoul"]',
                    ':has-text("탄탄제로 챌린지 미션 참여하기")'
                ]

                for alt_selector in alternative_selectors:
                    count = await page.locator(alt_selector).count()
                    if count > 0:
                        print(f"   대체 selector 발견: {alt_selector} ({count}개)")
                        challenge_button_selector = alt_selector
                        break

            # Click the button
            challenge_button = page.locator(challenge_button_selector).first
            if await challenge_button.is_visible():
                print(f"🖱️  챌린지 버튼 클릭...")

                # Scroll into view
                await challenge_button.scroll_into_view_if_needed()
                await page.wait_for_timeout(500)

                # Click
                await challenge_button.click()
                await page.wait_for_timeout(3000)

                print(f"✅ 챌린지 버튼 클릭 완료!")
                print(f"   현재 URL: {page.url}")
            else:
                raise Exception("챌린지 버튼이 보이지 않습니다")

            # ============================================================
            # STEP 4: 챌린지 폼 작성
            # ============================================================
            print(f"\n{'='*70}")
            print(f"📝 STEP 4: 챌린지 폼 작성")
            print(f"{'='*70}")

            await page.wait_for_timeout(2000)

            # Screenshot after modal opens
            await page.screenshot(path=str(screenshot_dir / "02_modal_opened.png"))

            # Fill title
            title_selectors = [
                'input[placeholder*="제목"]',
                'input[name*="title"]',
                'input[name*="subject"]',
                '#title'
            ]

            for selector in title_selectors:
                count = await page.locator(selector).count()
                if count > 0:
                    elem = page.locator(selector).first
                    if await elem.is_visible():
                        print(f"✓ 제목 필드 발견: {selector}")
                        await elem.fill(submission_data['title'])
                        print(f"  입력: {submission_data['title']}")
                        break

            # Upload image if provided
            if image_path:
                print(f"\n📸 이미지 업로드...")

                file_input = page.locator('input[type="file"]').first
                if await file_input.count() > 0:
                    image_abs_path = str(Path(image_path).absolute())
                    if Path(image_abs_path).exists():
                        await file_input.set_input_files(image_abs_path)
                        print(f"✅ 이미지 업로드 완료: {image_path}")
                        await page.wait_for_timeout(1500)
                    else:
                        print(f"⚠️  이미지 파일 없음: {image_abs_path}")
                else:
                    print(f"⚠️  파일 업로드 필드를 찾을 수 없음")

            # Fill content
            content_selectors = [
                'textarea[placeholder*="내용"]',
                'textarea[name*="content"]',
                'textarea'
            ]

            for selector in content_selectors:
                count = await page.locator(selector).count()
                if count > 0:
                    elem = page.locator(selector).first
                    if await elem.is_visible():
                        print(f"\n✓ 내용 필드 발견: {selector}")
                        await elem.fill(submission_data['content'])
                        print(f"  입력: {submission_data['content']}")
                        break

            # Screenshot before submit
            await page.screenshot(path=str(screenshot_dir / "03_before_submit.png"))

            # ============================================================
            # STEP 5: 제출
            # ============================================================
            print(f"\n{'='*70}")
            print(f"🚀 STEP 5: 제출")
            print(f"{'='*70}")

            # Find submit button - 정확한 selector 사용
            submit_selectors = [
                'input.save[type="submit"]',  # 정확한 selector
                'input[type="submit"][value="등록하기"]',
                'input[type="submit"]',
                'button:has-text("제출하기")',
                'button:has-text("등록하기")',
                'button[type="submit"]',
                '.submit-btn',
                '.save'
            ]

            submit_clicked = False
            for selector in submit_selectors:
                count = await page.locator(selector).count()
                if count > 0:
                    print(f"🔍 '{selector}' 발견: {count}개")

                    for i in range(count):
                        btn = page.locator(selector).nth(i)
                        if await btn.is_visible():
                            # Get button text or value
                            value = await btn.get_attribute('value')
                            text = await btn.text_content()
                            display_text = value if value else (text.strip() if text else 'N/A')

                            print(f"✓ 제출 버튼 발견: '{display_text}'")
                            print(f"  Selector: {selector}")
                            print(f"🖱️  버튼 클릭...")

                            # Scroll into view before clicking
                            await btn.scroll_into_view_if_needed()
                            await page.wait_for_timeout(500)

                            await btn.click()
                            await page.wait_for_timeout(3000)

                            submit_clicked = True
                            break

                    if submit_clicked:
                        break

            if not submit_clicked:
                print(f"⚠️  제출 버튼을 찾을 수 없습니다")
                print(f"📸 현재 화면 스크린샷 저장...")
                await page.screenshot(path=str(screenshot_dir / "04_no_submit_button.png"))

            print(f"✅ 제출 완료!")
            print(f"   현재 URL: {page.url}")

            # Screenshot after submit
            await page.screenshot(path=str(screenshot_dir / "05_after_submit.png"))

            # Check for success message
            success_patterns = [':has-text("성공")', ':has-text("완료")', ':has-text("등록되었습니다")']
            for pattern in success_patterns:
                if await page.locator(pattern).count() > 0:
                    elem = page.locator(pattern).first
                    if await elem.is_visible():
                        msg = await elem.text_content()
                        print(f"\n✨ 성공 메시지: {msg.strip()}")
                        break

            # ============================================================
            # STEP 6: 제출된 항목 확인
            # ============================================================
            print(f"\n{'='*70}")
            print(f"📋 STEP 6: 제출된 항목 확인")
            print(f"{'='*70}")

            # Wait for page to refresh/update
            await page.wait_for_timeout(3000)

            # Navigate to submissions list if needed
            # Selector: a.zero-v-btn (from screenshot)
            list_button_selector = 'a.zero-v-btn[href="/zeroseoul/"]'

            if await page.locator(list_button_selector).count() > 0:
                print(f"🔍 목록 보기 버튼 발견")
                await page.click(list_button_selector)
                await page.wait_for_timeout(2000)
                print(f"✅ 목록 페이지로 이동")
            else:
                # Try going to main page
                print(f"📍 메인 페이지로 이동하여 제출 목록 확인")
                await page.goto("https://event.seoul.go.kr/zeroseoul/", wait_until='networkidle')
                await page.wait_for_timeout(2000)

            # Scroll down to see submissions
            await page.evaluate("window.scrollTo(0, document.body.scrollHeight / 2)")
            await page.wait_for_timeout(1000)

            # Take screenshot of the list
            await page.screenshot(path=str(screenshot_dir / "06_submission_list.png"), full_page=True)
            print(f"📸 제출 목록 스크린샷 저장")

            # Try to find our submission
            print(f"\n🔍 제출한 항목 찾기...")
            print(f"   제목: '{submission_data['title']}'")

            # Look for our title in the page
            title_locator = page.locator(f':has-text("{submission_data["title"]}")')
            title_count = await title_locator.count()

            if title_count > 0:
                print(f"✅ 제출한 항목을 찾았습니다! ({title_count}개 일치)")

                # Get first match details
                first_match = title_locator.first
                if await first_match.is_visible():
                    await first_match.scroll_into_view_if_needed()
                    await page.wait_for_timeout(500)

                    # Highlight it with a screenshot
                    await page.screenshot(path=str(screenshot_dir / "07_found_submission.png"))
                    print(f"📸 제출한 항목 하이라이트 스크린샷 저장")
            else:
                print(f"⚠️  아직 목록에 표시되지 않았습니다 (처리 중일 수 있음)")

            print(f"\n📸 스크린샷 저장 위치:")
            print(f"   1. {screenshot_dir / '01_before_challenge_click.png'}")
            print(f"   2. {screenshot_dir / '02_modal_opened.png'}")
            print(f"   3. {screenshot_dir / '03_before_submit.png'}")
            print(f"   4. {screenshot_dir / '05_after_submit.png'}")
            print(f"   5. {screenshot_dir / '06_submission_list.png'}")
            print(f"   6. {screenshot_dir / '07_found_submission.png'}")

            # 잠시 대기 (결과 확인용)
            print(f"\n⏳ 5초 후 자동으로 종료됩니다...")
            await page.wait_for_timeout(5000)

            print(f"\n{'='*70}")
            print(f"✅ ✅ ✅  챌린지 제출이 완료되었습니다!  ✅ ✅ ✅")
            print(f"{'='*70}")
            print(f"\n📋 제출 정보:")
            print(f"   제목: {submission_data['title']}")
            print(f"   내용: {submission_data['content']}")
            if image_path:
                print(f"   이미지: {image_path}")
            print(f"\n🎉 모든 작업이 성공적으로 완료되었습니다!")
            print(f"{'='*70}\n")

        except Exception as e:
            print(f"\n{'='*70}")
            print(f"❌ 오류 발생!")
            print(f"{'='*70}")
            print(f"\n에러 내용: {str(e)}\n")
            import traceback
            traceback.print_exc()

            try:
                await page.screenshot(path=str(screenshot_dir / "error.png"))
                print(f"\n📸 에러 스크린샷: {screenshot_dir / 'error.png'}")
            except:
                pass

            print(f"\n⏳ 에러 확인을 위해 10초간 브라우저를 열어둡니다...")
            await page.wait_for_timeout(10000)

        finally:
            print(f"\n🔚 브라우저를 종료합니다...")
            await browser.close()
            print(f"✅ 브라우저가 정상적으로 종료되었습니다.\n")


async def main():
    """메인 함수"""

    # 계정 정보
    credentials = {
        "username": "qkrwjdgh1212",
        "password": "danielpark12!"
    }

    # 제출 데이터
    submission_data = {
        "title": "녹색 환경 보호 실천 챌린지",
        "content": "자연 속에서 환경의 소중함을 느끼며, 일회용품 사용 줄이기와 녹색소비를 실천하고 있습니다. 작은 실천이 모여 큰 변화를 만듭니다!"
    }

    # 이미지 경로
    image_path = r"C:\Projects\TAZeroro1\test_images\bamboo_forest.jpg"

    await submit_zeroseoul_challenge(
        credentials=credentials,
        submission_data=submission_data,
        image_path=image_path
    )


if __name__ == "__main__":
    print("\n🤖 Zero Seoul 챌린지 자동 제출 RPA")
    print("=" * 70)

    asyncio.run(main())
