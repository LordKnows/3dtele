"""Locate a Chrome / Chromium binary for the headless check scripts.

CHROME_BIN overrides the search; otherwise the macOS app, then google-chrome / chromium / chromium-browser on PATH.
CHROME_ARGS (whitespace-separated) is appended to every launch, e.g. to add proxy or host-resolver flags.
"""
import os
import shlex
import shutil
import sys

MAC_CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
CANDIDATES = ["google-chrome", "google-chrome-stable", "chromium", "chromium-browser"]


def find_chrome() -> str:
    env = os.environ.get("CHROME_BIN", "").strip()
    if env:
        return env
    if os.path.exists(MAC_CHROME):
        return MAC_CHROME
    for name in CANDIDATES:
        path = shutil.which(name)
        if path:
            return path
    sys.exit("Chrome not found: set CHROME_BIN or install google-chrome / chromium")


def chrome_cmd(*args: str) -> list[str]:
    """The binary plus flags every headless run needs; extra args follow."""
    cmd = [find_chrome()]
    if sys.platform.startswith("linux") and hasattr(os, "geteuid") and os.geteuid() == 0:
        cmd.append("--no-sandbox")  # Chrome refuses to start as root with the sandbox on
    cmd += shlex.split(os.environ.get("CHROME_ARGS", ""))
    return cmd + list(args)
