# Insurance Refund Bot

Automate insurance refund filing using [Playwright](https://playwright.dev/python/) browser automation. The bot logs into the insurance website with your credentials, enters a dynamic authenticator code, fills in the refund form, uploads two files, and submits — all hands-free.

## Prerequisites

- **Python 3.9+**
- A copy of the login credentials for the insurance website

## Quick Start

### 1. Install dependencies

```bash
cd insurance-refund-bot
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
playwright install chromium
```

### 2. Configure credentials (one-time)

```bash
cp .env.example .env
```

Edit `.env` and fill in:

| Variable             | Description                                  |
|----------------------|----------------------------------------------|
| `INSURANCE_URL`      | Login page URL of the insurance site         |
| `INSURANCE_USERNAME` | Your username / email                        |
| `INSURANCE_PASSWORD` | Your password                                |
| `BROWSER_MODE`       | `headed` (see browser) or `headless` (hidden)|

> **Security:** The `.env` file is git-ignored and never committed.

### 3. Adapt selectors to your insurance website

Open `refund_bot.py` and update the CSS selectors marked with `# TODO: adapt selector` to match the actual HTML elements on your insurance company's website.

**Tip — record selectors automatically:**

```bash
playwright codegen https://www.your-insurance-site.com
```

This opens a browser and generates selector code as you click through the site.

### 4. Run

```bash
python run.py path/to/receipt.pdf path/to/medical_report.pdf
```

You will be prompted for the authenticator code. Alternatively, pass it directly:

```bash
python run.py receipt.pdf report.pdf --auth-code 123456
```

### 5. Confirm

After the run completes, a confirmation screenshot is saved in the `screenshots/` directory.

## Project Structure

```
insurance-refund-bot/
├── .env.example      # Credential template (copy to .env)
├── config.py         # Loads .env, exposes settings
├── refund_bot.py     # Core Playwright automation logic
├── run.py            # CLI entry-point
├── requirements.txt  # Python dependencies
├── screenshots/      # Auto-created; stores run screenshots
└── README.md         # This file
```

## How It Works

1. **Login** — navigates to the insurance site and submits username + password.
2. **2FA** — enters the authenticator code you provide at runtime.
3. **Navigate** — goes to the refund / claim form.
4. **Fill & Upload** — fills form fields and attaches your two files.
5. **Submit** — clicks submit and captures a confirmation screenshot.

At every step a screenshot is saved so you can verify what happened.

## Troubleshooting

| Problem | Fix |
|---------|-----|
| `playwright install` fails | Run `playwright install --with-deps chromium` |
| Bot can't find an element | Update the CSS selector in `refund_bot.py` |
| Site detects automation | Set `BROWSER_MODE=headed` and increase delays in `_human_delay()` |
| Authenticator code rejected | Make sure you enter the code quickly — some expire in 30 seconds |

## Security Notes

- Credentials are stored **only** in your local `.env` file (git-ignored).
- The authenticator code is entered at runtime and never stored.
- Screenshots may contain personal data — the `screenshots/` folder is also git-ignored.
