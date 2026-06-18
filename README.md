# 🚀 YoriChecker - Advanced Crunchyroll Login Checker

An advanced CLI tool to check Crunchyroll login credentials with automatic directory management, file processing, and detailed result tracking.

## ✨ Features

- **Smart Directory Management**: Automatically creates `~/YORICHECKER/` and `~/YORICHECKER/RESULTS/` directories
- **Flexible Input Formats**: Supports `email:password`, `email password`, or `email;password` in files
- **File-Based Processing**: Place credential files in `YORICHECKER/` folder and process them with simple commands
- **Detailed Result Tracking**: Saves timestamped results to `YORICHECKER/RESULTS/`
- **Medium Speed Processing**: Built-in delays between checks to avoid rate limiting
- **Privacy Focused**: Emails masked in output (shows first 3 chars + ***@domain)
- **Cross-Platform**: Works on Windows, macOS, Linux, and Termux (Android)
- **No Screenshots**: Clean terminal-only operation

## 📦 Installation

### From GitHub (Recommended)
```bash
pip install git+https://github.com/harshi79/yorichecker.git
```

### From Local Source
```bash
pip install -e .  # From the cloned repository directory
```

### First-Time Setup
After installation, run:
```bash
yorichecker init
```
This creates the required directory structure:
- `~/YORICHECKER/` - Place your credential files here
- `~/YORICHECKER/RESULTS/` - Where results will be saved

## 🚀 Usage

### Basic Commands
```bash
yorichecker init                          # Create directory structure (run once)
yorichecker check email@example.com pass  # Check single account
yorichecker check accounts.txt            # Check accounts in YORICHECKER/accounts.txt
yorichecker help                          # Show detailed help
yorichecker version                       # Show version information
```

### File Format
Place your credential files in `~/YORICHECKER/` with one account per line:
```
email@example.com:password123
test@domain.com pass456
user@site.org;password789
```
The tool automatically detects `:`, space, or `;` as delimiters.

### Example Workflow
```bash
# 1. Install and initialize
pip install git+https://github.com/harshi79/yorichecker.git
yorichecker init

# 2. Place your file in YORICHECKER
#    (e.g., copy accounts.txt to ~/YORICHECKER/accounts.txt)

# 3. Process the file
yorichecker check accounts.txt

# 4. View results
#    Check ~/YORICHECKER/RESULTS/ for timestamped result files
```

## 📁 Directory Structure
After running `yorichecker init`:
```
~/YORICHECKER/
├── accounts.txt          ← Your credential files go here
├── more_accounts.txt
└── RESULTS/
    ├── accounts_results_20260619_143022.txt
    └── more_accounts_results_20260619_143510.txt
```

## 📊 Output Examples

**Single Account Check:**
```
$ yorichecker check user@example.com mypassword
🔍 Checking single account: use***@example.com
Please wait 30-40 seconds...

✅ use***@example.com: SUCCESS - Login Successful!
💾 Result saved to: /home/user/YORICHECKER/RESULTS/single_user_at_example_20260619_143022.txt
```

**File Processing:**
```
$ yorichecker check accounts.txt
📂 Processing file: accounts.txt
📁 Looking in: /home/user/YORICHECKER/
🔍 Processing line 1: use***@example.com
🔍 Processing line 2: tes***@example.com
🔍 Processing line 3: admin***@example.com

📊 Processing complete: 2/3 successful logins
💾 Detailed results saved to: /home/user/YORICHECKER/RESULTS/accounts_results_20260619_143022.txt
📁 Results directory: /home/user/YORICHECKER/RESULTS/
```

**Result File Contents:**
```
Crunchyroll Checker Results
Source file: accounts.txt
Processed at: 2026-06-19 14:30:22
Total accounts: 3
--------------------------------------------------

1. use***@example.com: SUCCESS - Login Successful!
2. tes***@example.com: FAILED - Wrong email or password
   Details: Wrong email or password
3. admin***@example.com: SUCCESS - Login Successful!
```

## 🔧 Configuration

### Browser Mode
- By default runs in headless mode (no browser UI)
- Use `--no-headless` to see the browser during checks:
  ```bash
  yorichecker check email@example.com password --no-headless
  ```

### Speed Control
Processing includes a 2-second delay between account checks to maintain medium speed and avoid triggering security measures.

## 🛑 Stopping Processing
During file processing, press `Ctrl+C` to safely stop the operation. Results processed up to that point will be saved.

## 📱 Termux (Android) Setup
1. Install Termux from F-Droid or Play Store
2. Run: `pkg update && pkg upgrade`
3. Install dependencies: `pkg install python python-pip git`
4. Install YoriChecker: `pip install git+https://github.com/harshi79/yorichecker.git`
5. Initialize: `yorichecker init`
6. Install Playwright: `playwright install chromium`
7. Place files in `~/YORICHECKER/` and process as usual

## ⚠️ Security Notes
- For security, consider using temporary/test credentials
- The tool does not store any credentials between runs
- All processing happens locally - no data leaves your machine
- Use only with accounts you own or have explicit permission to test

## 📝 License
MIT License - see `LICENSE` file for details.

## 🐛 Troubleshooting

### "File not found" Error
- Remember to place files in `~/YORICHECKER/` directory
- Run `yorichecker init` first to create directories
- Filenames are case-sensitive on some systems

### Playwright Errors
- Run `playwright install chromium` if missing
- Ensure you have internet access for initial browser download

### No Results Being Saved
- Check that `~/YORICHECKER/RESULTS/` directory exists
- Verify write permissions to your home directory

## 🙏 Support
For issues or feature requests, visit:
https://github.com/harshi79/yorichecker/issues