"""Render every page of site/ in headless Chrome and report console errors plus a DOM summary.

Usage:
  python3 check_render.py                      # all pages
  python3 check_render.py guided classics      # only these pages (file stem)
  python3 check_render.py --shot guided:1400x1600[:light]   # also screenshot a page (mobile: 390x844)
"""
import os
import re
import signal
import subprocess
import sys
import tempfile
from pathlib import Path

CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
SITE = Path(__file__).resolve().parent / "site"
COUNTS = {
    "sections": r"<section id=", "concepts": r'class="concept"', "steps": r'class="step"', "classics": r'class="classic"',
    "adv": r'class="card-d"', "diagrams": r'class="diagram"', "lane dots": r'<g class="m"', "mjx": r"<mjx-container",
    "chips": r'class="cchip', "idrefs": r'class="idref"', "stages": r'class="stage"', "glossary rows": r'<td class="en">',
    "db rows": r'<td class="y">', "ideas": r'class="idea"', "areas": r'class="area"', "nav pages": r'class="page', "pager": r'class="pager"',
}


def run_chrome(extra_args, wait_s):
    # Output goes to files and the whole process group is killed on timeout: Chrome helpers can keep a pipe open.
    with tempfile.TemporaryDirectory() as prof, tempfile.TemporaryFile() as so, tempfile.TemporaryFile() as se:
        args = [CHROME, "--headless=new", "--disable-gpu", "--no-first-run", "--no-default-browser-check",
                "--disable-extensions", f"--user-data-dir={prof}", "--enable-logging=stderr", "--v=0"] + extra_args
        proc = subprocess.Popen(args, stdout=so, stderr=se, start_new_session=True)
        try:
            proc.wait(timeout=wait_s)
        except subprocess.TimeoutExpired:
            os.killpg(proc.pid, signal.SIGKILL)
            proc.wait()
        so.seek(0)
        se.seek(0)
        return so.read().decode("utf-8", "replace"), se.read().decode("utf-8", "replace")


def check(page: Path) -> bool:
    dom, err = run_chrome(["--timeout=20000", "--dump-dom", page.as_uri()], 40)
    errors = [l for l in err.splitlines() if "CONSOLE" in l and "chrome-extension" not in l]
    counts = {k: len(re.findall(v, dom)) for k, v in COUNTS.items()}
    shown = ", ".join(f"{k}={v}" for k, v in counts.items() if v)
    print(f"{page.name:18s} dom={len(dom) // 1024}KB  {shown}")
    for e in errors[:10]:
        print("   console:", e[:300])
    return not errors and len(dom) > 1000


def screenshot(spec: str):
    parts = spec.split(":")
    stem, size = parts[0], (parts[1] if len(parts) > 1 else "1400x1600")
    scheme = parts[2] if len(parts) > 2 else ""
    w, _, h = size.partition("x")
    shot = SITE.parent / f"shot-{stem}-{w}{'-' + scheme if scheme else ''}.png"
    flags = [f"--window-size={w},{h}", "--hide-scrollbars", "--virtual-time-budget=15000", f"--screenshot={shot}"]
    if scheme == "light":
        flags.append("--blink-settings=preferredColorScheme=1")
    run_chrome(flags + [(SITE / f"{stem}.html").as_uri()], 60)
    print("screenshot", shot, shot.exists())


def main() -> int:
    args = sys.argv[1:]
    shots = [args[i + 1] for i, a in enumerate(args) if a == "--shot" and i + 1 < len(args)]
    stems = [a for i, a in enumerate(args) if a != "--shot" and (i == 0 or args[i - 1] != "--shot")]
    pages = [SITE / f"{s}.html" for s in stems] if stems else sorted(SITE.glob("*.html"))
    ok = all([check(p) for p in pages])
    for s in shots:
        screenshot(s)
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
