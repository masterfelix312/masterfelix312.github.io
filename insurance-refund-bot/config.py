"""Configuration management for the insurance refund bot."""

import os
import sys
from pathlib import Path

from dotenv import load_dotenv

# Load .env from the project directory
_env_path = Path(__file__).resolve().parent / ".env"
load_dotenv(_env_path)


def _require_env(name: str) -> str:
    """Return an environment variable or exit with a clear error."""
    value = os.getenv(name)
    if not value:
        sys.exit(
            f"Error: environment variable '{name}' is not set.\n"
            f"Copy .env.example to .env and fill in your credentials."
        )
    return value


# --- Credentials (loaded once from .env) ---
INSURANCE_URL: str = _require_env("INSURANCE_URL")
INSURANCE_USERNAME: str = _require_env("INSURANCE_USERNAME")
INSURANCE_PASSWORD: str = _require_env("INSURANCE_PASSWORD")

# --- Browser settings ---
BROWSER_HEADLESS: bool = os.getenv("BROWSER_MODE", "headed").lower() == "headless"

# --- Directories ---
SCREENSHOTS_DIR: Path = Path(__file__).resolve().parent / "screenshots"
SCREENSHOTS_DIR.mkdir(exist_ok=True)
