# Yori Checker

A CLI tool to check Crunchyroll account credentials.

## Features

- Check single Crunchyroll account credentials
- Process multiple accounts from a file
- Automatic directory creation (`~/YORICHECKER/`)
- Timestamped result tracking
- Medium-speed processing to avoid rate limiting
- Privacy protection (email masking in output)
- Cross-platform compatibility (Windows, macOS, Linux, Termux)
- Cloudflare bypass automation
- Cookie consent handling

## Installation

```bash
# Install from GitHub
pip install git+https://github.com/harshi79/yorichecker.git

# Or install locally
pip install -e .
```

## Usage

### Initial Setup

```bash
# Create the required directory structure
yorichecker init
```

### Check Single Account

```bash
yorichecker check email@example.com password123
```

### Check Multiple Accounts from File

1. Place your credential file in `~/YORICHECKER/` (supports `email:password`, `email password`, or `email;password` formats)
2. Run:
```bash
yorichecker check accounts.txt
```

### View Help

```bash
yorichecker help
```

### Check Version

```bash
yorichecker version
```

## Output

- Results are saved to `~/YORICHECKER/RESULTS/` as timestamped text files
- Emails are masked in output for privacy (e.g., `joh***@example.com`)
- Each result includes status (SUCCESS/FAILED) and a descriptive message

## Examples

```bash
# Initialize directories
yorichecker init

# Check a single account
yorichecker check user@example.com mypassword

# Check accounts from a file (place accounts.txt in ~/YORICHECKER/)
yorichecker check accounts.txt
```

## License

MIT License