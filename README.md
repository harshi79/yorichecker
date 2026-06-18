# Crunchyroll Login Checker (CLI Version)

A command-line tool to test Crunchyroll login credentials using Playwright for browser automation. This version runs directly in terminal/Termux without Telegram dependencies.

## Features
- Automated Crunchyroll login with Cloudflare bypass
- Incognito mode browsing (no cache/cookies preserved)
- Screenshot saving for debugging (optional)
- Works in Linux, Windows, macOS, and Termux (Android)
- Simple CLI interface

## Installation

### From GitHub (Direct)
```bash
pip install git+https://github.com/yourusername/yorichecker.git
```

### From PyPI (Once published)
```bash
pip install yorichecker
```

### Install Playwright Browser (Required)
```bash
playwright install chromium
```

## Usage

### Basic Command
```bash
yorichecker --email your_email@example.com --password your_password
```

### Options
- `--email`: Crunchyroll email address (required for single mode)
- `--file`: Path to txt file containing email password pairs (one per line) - for batch mode
- `--password`: Crunchyroll password (required for single mode)
- `--headless`: Run browser in background (default: true)
- `--no-headless`: Show browser UI (useful for debugging)

### Examples

**Single account:**
```bash
yorichecker --email user@example.com --password mypassword123
```

**Batch processing (from file):**
```bash
yorichecker --file accounts.txt
```

*(File format: `email password` per line, passwords can contain spaces)*

### Sample Output
```
Processing single account: use***@example.com
Please wait 30-40 seconds...

✅ SUCCESS: Login Successful!
```

### Termux (Android) Specific Instructions

1. Install Termux from F-Droid or Play Store
2. Update packages: `pkg update && pkg upgrade`
3. Install Python and pip: `pkg install python python-pip`
4. Install git (to clone): `pkg install git`
5. Install the package: `pip install git+https://github.com/yourusername/yorichecker.git`
6. Install Playwright: `playwright install chromium`
7. Run as shown above

## How It Works
- Launches Chromium browser in incognito mode
- Navigates to Crunchyroll SSO login page
- Handles Cloudflare protection if encountered
- Fills login credentials and submits form
- Checks for login success/failure
- Reports results to terminal

## Notes
- For security, consider using temporary/test credentials
- The tool does not store any credentials between runs
- Headless mode is recommended for server/terminal usage
- Use `--no-headless` if you need to visually debug login issues

## Security Disclaimer
This tool is intended for legitimate testing of your own Crunchyroll credentials. Unauthorized access to accounts is illegal and violates Crunchyroll's Terms of Service. Use only with permission.