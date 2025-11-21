"""
Debug script for ZeroSeoul RPA - Step by step execution
"""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from playwright.async_api import async_playwright


async def test_rpa_step_by_step():
    """Test each RPA step individually"""

    print("=" * 70)
    print("ZeroSeoul RPA Debug Test - Step by Step")
    print("=" * 70)

    async with async_playwright() as playwright:
        # Launch browser
        print("\n[Step 1] Launching browser...")
        browser = await playwright.chromium.launch(
            headless=False,
            slow_mo=1000
        )

        context = await browser.new_context(
            viewport={'width': 1920, 'height': 1080}
        )
        page = await context.new_page()

        try:
            # Step 2: Navigate to login page
            print("[Step 2] Navigating to login page...")
            login_url = "https://event.seoul.go.kr/zeroseoul/login"
            await page.goto(login_url)
            await page.wait_for_load_state('networkidle')
            print(f"✅ Current URL: {page.url}")

            # Step 2.5: Close all today popups if exist
            print("[Step 2.5] Checking for today-close popups...")
            today_close_selector = "button.today-close:visible"
            await page.wait_for_timeout(1000)  # Wait for popup to appear

            # Close popups one by one, re-checking after each click
            closed_count = 0
            while True:
                buttons = await page.locator(today_close_selector).all()
                if len(buttons) == 0:
                    break
                print(f"   Closing popup {closed_count + 1}...")
                await buttons[0].click()  # Always click the first one
                await page.wait_for_timeout(500)
                closed_count += 1

            if closed_count > 0:
                print(f"✅ {closed_count} popup(s) closed")
            else:
                print("   No visible today popup found")

            # Step 3: Fill login form
            print("[Step 3] Filling login form...")
            username_selector = "input[placeholder*='아이디']"
            password_selector = "input[type='password']"

            await page.locator(username_selector).fill("cjh030808")
            await page.locator(password_selector).fill("@m1718m172")
            print("✅ Login credentials filled")

            # Step 4: Click login button
            print("[Step 4] Clicking login button...")
            submit_selector = "button:has-text('로그인하기')"
            await page.locator(submit_selector).click()
            await page.wait_for_timeout(2000)
            print(f"✅ After login URL: {page.url}")

            # Step 5: Navigate to form URL
            print("[Step 5] Navigating to form page...")
            form_url = "https://event.seoul.go.kr/zeroseoul/"
            await page.goto(form_url)
            await page.wait_for_load_state('networkidle')
            print(f"✅ Current URL: {page.url}")

            # Step 5.5: Close all today popups if exist
            print("[Step 5.5] Checking for today-close popups...")
            today_close_selector = "button.today-close:visible"
            await page.wait_for_timeout(1000)  # Wait for popup to appear

            # Close popups one by one, re-checking after each click
            closed_count = 0
            while True:
                buttons = await page.locator(today_close_selector).all()
                if len(buttons) == 0:
                    break
                print(f"   Closing popup {closed_count + 1}...")
                await buttons[0].click()  # Always click the first one
                await page.wait_for_timeout(500)
                closed_count += 1

            if closed_count > 0:
                print(f"✅ {closed_count} popup(s) closed")
            else:
                print("   No visible today popup found")

            # Step 6: Open modal
            print("[Step 6] Opening mission modal...")
            modal_trigger = "a[href='/zeroseoul/']:has-text('미션인증하기')"

            # Check if trigger exists
            trigger_count = await page.locator(modal_trigger).count()
            print(f"   Found {trigger_count} modal trigger(s)")

            if trigger_count > 0:
                await page.locator(modal_trigger).click()
                await page.wait_for_timeout(1000)
                print("✅ Modal opened")
            else:
                print("❌ Modal trigger not found!")
                # Try alternative selector
                print("   Trying alternative: link with text '미션인증하기'")
                alt_trigger = page.get_by_role('link', name='미션인증하기')
                if await alt_trigger.count() > 0:
                    await alt_trigger.click()
                    await page.wait_for_timeout(1000)
                    print("✅ Modal opened (alternative method)")

            # Step 7: Fill form
            print("[Step 7] Filling mission form...")

            # Title
            title_selector = "input[placeholder='제목을 입력하세요']"
            title_count = await page.locator(title_selector).count()
            print(f"   Title input found: {title_count}")
            if title_count > 0:
                await page.locator(title_selector).fill("오래된 옷도 잘 수선해서 입었어요~")
                print("   ✅ Title filled")

            # Content
            content_selector = "textarea[placeholder='내용을 입력하세요']"
            content_count = await page.locator(content_selector).count()
            print(f"   Content textarea found: {content_count}")
            if content_count > 0:
                await page.locator(content_selector).fill("환경에 진심인 저는 옷 한 번을 사도 오래오래 수선해서 입는답니다^^! 우리 함께 동참하길 ~")
                print("   ✅ Content filled")

            # Photo upload
            photo_selector = "input[type='file']"
            photo_count = await page.locator(photo_selector).count()
            print(f"   Photo input found: {photo_count}")
            if photo_count > 0:
                test_image = Path(__file__).parent / "fixtures" / "mission_photo.jpg"
                await page.locator(photo_selector).set_input_files(str(test_image.absolute()))
                print(f"   ✅ Photo uploaded: {test_image.name}")

            # Step 8: Find submit button
            print("[Step 8] Finding submit button...")

            # Try multiple selectors
            submit_selectors = [
                "button:has-text('등록하기')",
                "button:has-text('등록')",
                "button[type='submit']:visible",
            ]

            submit_button = None
            for selector in submit_selectors:
                count = await page.locator(selector).count()
                print(f"   Trying '{selector}': found {count}")
                if count > 0:
                    submit_button = page.locator(selector).first
                    print(f"   ✅ Submit button found with: {selector}")
                    break

            if not submit_button:
                # Try using getByRole
                print("   Trying getByRole('button', name='등록하기')...")
                submit_button = page.get_by_role('button', name='등록하기')
                if await submit_button.count() > 0:
                    print("   ✅ Submit button found with getByRole")

            # Step 9: Click submit button
            if submit_button and await submit_button.count() > 0:
                print("[Step 9] Clicking submit button...")
                await submit_button.click()
                await page.wait_for_timeout(2000)

                # Check for success or error
                print("[Step 10] Checking result...")

                # Wait for any dialogs
                await page.wait_for_timeout(1000)

                print(f"✅ Final URL: {page.url}")
                print("\n🎉 RPA Test completed! Check browser for result.")

            else:
                print("❌ Submit button not found!")

            # Keep browser open for inspection
            print("\n⏸️  Browser will stay open for 30 seconds for inspection...")
            await page.wait_for_timeout(30000)

        except Exception as e:
            print(f"\n❌ Error: {e}")
            import traceback
            traceback.print_exc()
            await page.wait_for_timeout(10000)

        finally:
            await browser.close()
            print("\n✅ Browser closed")


if __name__ == "__main__":
    asyncio.run(test_rpa_step_by_step())
