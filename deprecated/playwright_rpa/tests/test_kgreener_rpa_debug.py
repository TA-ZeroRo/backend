"""
Debug script for K-Greener RPA - Step by step execution
"""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from playwright.async_api import async_playwright


async def test_kgreener_rpa_step_by_step():
    """Test each RPA step individually for K-Greener campaign"""

    print("=" * 70)
    print("K-Greener RPA Debug Test - Step by Step")
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
            login_url = "https://k-greener.com/login"
            await page.goto(login_url)
            await page.wait_for_load_state('networkidle')
            print(f"✅ Current URL: {page.url}")

            # Step 3: Fill login form
            print("[Step 3] Filling login form...")
            username_selector = "input[name='uid']"
            password_selector = "input[name='passwd']"

            await page.locator(username_selector).fill("goodjjh1234@gmail.com")
            await page.locator(password_selector).fill("@M1718m172")
            print("✅ Login credentials filled")

            # Step 4: Click login button
            print("[Step 4] Clicking login button...")
            submit_selector = "button.btn.btn-primary.btn-block"
            await page.locator(submit_selector).click()
            await page.wait_for_timeout(2000)
            print(f"✅ After login URL: {page.url}")

            # Step 5: Navigate to form URL
            print("[Step 5] Navigating to form page...")
            form_url = "https://k-greener.com/act/?q=YToxOntzOjEyOiJrZXl3b3JkX3R5cGUiO3M6MzoiYWxsIjt9&board=b20231107865240d640e7f&bmode=write&back_url=L2FjdA%3D%3D"
            await page.goto(form_url)
            await page.wait_for_load_state('networkidle')
            print(f"✅ Current URL: {page.url}")

            # Step 6: Fill form
            print("[Step 6] Filling mission form...")

            # Category (Dropdown)
            category_selector = ".div_select.category_select"
            category_count = await page.locator(category_selector).count()
            print(f"   Category dropdown found: {category_count}")
            if category_count > 0:
                # Click category dropdown
                await page.locator(category_selector).click()
                await page.wait_for_timeout(500)
                print("   ✅ Category dropdown opened")

                # Click "자유게시판" option
                await page.get_by_role('listitem').filter(has_text='자유게시판').click()
                await page.wait_for_timeout(500)
                print("   ✅ Category selected: 자유게시판")

            # Title
            title_selector = "input[name='subject']"
            title_count = await page.locator(title_selector).count()
            print(f"   Title input found: {title_count}")
            if title_count > 0:
                await page.locator(title_selector).fill("환경보호 실천 - 재활용 분리수거 철저히!")
                print("   ✅ Title filled")

            # Content (Rich Text Editor)
            content_selector = ".fr-element.fr-view"
            content_count = await page.locator(content_selector).count()
            print(f"   Content editor found: {content_count}")
            if content_count > 0:
                # For contenteditable div, we need to use JavaScript
                await page.locator(content_selector).click()
                await page.locator(content_selector).fill(
                    "오늘도 열심히 분리수거를 했습니다! "
                    "플라스틱, 종이, 캔을 각각 분리해서 버렸어요. "
                    "작은 실천이지만 지구를 위한 큰 걸음이라고 생각합니다. "
                    "함께 환경보호에 동참해요! 💚🌍"
                )
                print("   ✅ Content filled")

            # Photo upload
            photo_selector = "input[name='post_images[]']"
            photo_count = await page.locator(photo_selector).count()
            print(f"   Photo input found: {photo_count}")
            if photo_count > 0:
                test_image = Path(__file__).parent / "fixtures" / "mission_photo.jpg"
                # Use the first file input (for images)
                await page.locator(photo_selector).first.set_input_files(str(test_image.absolute()))
                print(f"   ✅ Photo uploaded: {test_image.name}")

            # Step 7: Click submit button
            print("[Step 7] Clicking submit button...")
            submit_selector = "button._save_post"
            submit_count = await page.locator(submit_selector).count()
            print(f"   Submit button found: {submit_count}")

            if submit_count > 0:
                await page.locator(submit_selector).click()
                await page.wait_for_timeout(2000)
                print("   ✅ Submit button clicked")

                # Check for success or error
                print("[Step 8] Checking result...")

                # Wait for any dialogs or navigation
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
    asyncio.run(test_kgreener_rpa_step_by_step())
