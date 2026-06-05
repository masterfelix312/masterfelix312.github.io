#!/usr/bin/env python3
"""
CLI entry-point for the Insurance Refund Bot.

Usage
-----
    python run.py <file1> <file2>

You will be prompted for the authenticator code at runtime.
Credentials are read from the .env file (see .env.example).
"""

from __future__ import annotations

import argparse
import getpass
import sys
from pathlib import Path

import refund_bot


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Automate insurance refund filing via browser automation.",
    )
    parser.add_argument(
        "file1",
        type=Path,
        help="Path to the first file to upload (e.g. receipt or invoice).",
    )
    parser.add_argument(
        "file2",
        type=Path,
        help="Path to the second file to upload (e.g. medical report).",
    )
    parser.add_argument(
        "--auth-code",
        type=str,
        default=None,
        help="Authenticator code. If omitted you will be prompted interactively.",
    )
    parser.add_argument(
        "--headless",
        action="store_true",
        default=False,
        help="Run browser in headless mode (no visible window).",
    )
    return parser.parse_args()


def main() -> None:
    args = _parse_args()

    # Validate files exist
    for f in (args.file1, args.file2):
        if not f.is_file():
            sys.exit(f"Error: file not found — {f}")

    # Override headless from CLI flag if supplied
    if args.headless:
        import config
        config.BROWSER_HEADLESS = True

    # Prompt for authenticator code if not provided via CLI
    auth_code = args.auth_code
    if not auth_code:
        auth_code = getpass.getpass("Enter authenticator code: ")
        if not auth_code.strip():
            sys.exit("Error: authenticator code cannot be empty.")

    print("=" * 50)
    print("  Insurance Refund Bot")
    print("=" * 50)
    print(f"  File 1 : {args.file1}")
    print(f"  File 2 : {args.file2}")
    print(f"  Auth   : {'*' * len(auth_code)}")
    print("=" * 50)

    refund_bot.run(
        file1=args.file1.resolve(),
        file2=args.file2.resolve(),
        auth_code=auth_code.strip(),
    )


if __name__ == "__main__":
    main()
