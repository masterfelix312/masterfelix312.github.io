"""
Insurance Refund Bot — Playwright-based browser automation.

This module contains the core automation logic.  It is intentionally written
as a *template*: you will need to adapt the CSS selectors and navigation
steps to match the actual insurance company website.

Places marked with "# TODO: adapt selector" must be customised once you
inspect the real website (use Playwright codegen to record selectors).
"""

from __future__ import annotations

import datetime
import time
from pathlib import Path
from typing import Optional

from playwright.sync_api import Page, sync_playwright, TimeoutError as PwTimeout

import config


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _human_delay(seconds: float = 0.8) -> None:
    """Sleep briefly to mimic human interaction and avoid bot detection."""
    time.sleep(seconds)


def _screenshot(page: Page, label: str) -> Path:
    """Save a timestamped screenshot and return its path."""
    ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    path = config.SCREENSHOTS_DIR / f"{label}_{ts}.png"
    page.screenshot(path=str(path), full_page=True)
    return path


# ---------------------------------------------------------------------------
# Core steps
# ---------------------------------------------------------------------------

def login(page: Page) -> None:
    """Navigate to the login page and authenticate with stored credentials."""
    print(f"[1/5] Navigating to {config.INSURANCE_URL} …")
    page.goto(config.INSURANCE_URL, wait_until="networkidle")
    _human_delay()

    # TODO: adapt selector — username field
    page.fill('input[name="username"], input[id="username"], input[type="email"]',
              config.INSURANCE_USERNAME)
    _human_delay(0.4)

    # TODO: adapt selector — password field
    page.fill('input[name="password"], input[id="password"], input[type="password"]',
              config.INSURANCE_PASSWORD)
    _human_delay(0.4)

    # TODO: adapt selector — login button
    page.click('button[type="submit"], input[type="submit"]')
    page.wait_for_load_state("networkidle")
    _screenshot(page, "after_login")
    print("       ✓ Login submitted.")


def enter_authenticator_code(page: Page, code: str) -> None:
    """Enter the dynamic authenticator / 2FA code."""
    print("[2/5] Entering authenticator code …")
    _human_delay()

    # TODO: adapt selector — authenticator code input
    page.fill('input[name="otp"], input[name="code"], input[name="totp"], '
              'input[id="authenticator"], input[aria-label*="code"]',
              code)
    _human_delay(0.4)

    # TODO: adapt selector — verify / confirm button
    page.click('button[type="submit"], button:has-text("Verify"), '
               'button:has-text("Confirm"), button:has-text("Submit")')
    page.wait_for_load_state("networkidle")
    _screenshot(page, "after_2fa")
    print("       ✓ Authenticator code accepted.")


def navigate_to_refund_form(page: Page) -> None:
    """Navigate from the dashboard to the refund / claim filing page."""
    print("[3/5] Navigating to refund form …")
    _human_delay()

    # TODO: adapt — click through menus / links to reach the refund form.
    # Examples (uncomment and adjust the one that matches your site):
    #   page.click('a:has-text("Claims")')
    #   page.click('a:has-text("Submit Refund")')
    #   page.goto("https://www.example-insurance.com/claims/new")

    page.wait_for_load_state("networkidle")
    _screenshot(page, "refund_form")
    print("       ✓ Refund form loaded.")


def fill_and_upload(
    page: Page,
    file1: Path,
    file2: Path,
    extra_fields: Optional[dict[str, str]] = None,
) -> None:
    """Fill in the refund form fields and upload the two required files."""
    print("[4/5] Filling form and uploading files …")
    _human_delay()

    # --- Optional extra fields (e.g. claim amount, description) ----------
    if extra_fields:
        for selector, value in extra_fields.items():
            page.fill(selector, value)
            _human_delay(0.3)

    # --- File uploads -----------------------------------------------------
    # TODO: adapt selector — first file upload input
    page.set_input_files(
        'input[type="file"]',  # adjust if there are multiple file inputs
        [str(file1), str(file2)],
    )
    _human_delay()

    _screenshot(page, "form_filled")
    print("       ✓ Form filled, files attached.")


def submit_refund(page: Page) -> Path:
    """Submit the refund form and capture confirmation."""
    print("[5/5] Submitting refund …")
    _human_delay()

    # TODO: adapt selector — submit / send button on the refund form
    page.click('button[type="submit"], button:has-text("Submit"), '
               'button:has-text("Send")')

    try:
        page.wait_for_load_state("networkidle", timeout=15_000)
    except PwTimeout:
        pass  # some sites redirect slowly; we still capture the screenshot

    screenshot_path = _screenshot(page, "confirmation")
    print(f"       ✓ Refund submitted. Confirmation screenshot: {screenshot_path}")
    return screenshot_path


# ---------------------------------------------------------------------------
# Orchestrator
# ---------------------------------------------------------------------------

def run(
    file1: Path,
    file2: Path,
    auth_code: str,
    extra_fields: Optional[dict[str, str]] = None,
) -> None:
    """Execute the full refund-filing workflow."""
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=config.BROWSER_HEADLESS)
        context = browser.new_context()
        page = context.new_page()

        try:
            login(page)
            enter_authenticator_code(page, auth_code)
            navigate_to_refund_form(page)
            fill_and_upload(page, file1, file2, extra_fields)
            submit_refund(page)
            print("\n✅ Refund filing complete!")
        except Exception as exc:
            err_shot = _screenshot(page, "error")
            print(f"\n❌ Error during automation: {exc}")
            print(f"   Screenshot saved: {err_shot}")
            raise
        finally:
            context.close()
            browser.close()
