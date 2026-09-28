"""Render the built page in headless Chrome, report console errors and a DOM summary; optional screenshots."""
import re
import subprocess
import sys
import tempfile
import time
from pathlib import Path

CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
PAGE = Path(__file__).resolve().parent / "telepresence-atlas.html"
SECTIONS = ["top", "summary", "roadmap", "foundations", "guided", "advanced", "classics", "glossary",
            "reading", "anchors", "map", "paradigms", "areas", "papers", "trends", "ideas", "method"]


def run_chrome(extra_args, wait_s):
    with tempfile.TemporaryDirectory() as prof:
        args = [CHROME, "--headless=new", "--disable-gpu", "--no-first-run", "--no-default-browser-check",
                "--disable-extensions", f"--user-data-dir={prof}", "--enable-logging=stderr", "--v=0"] + extra_args
        proc = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        try:
            out, err = proc.communicate(timeout=wait_s)
        except subprocess.TimeoutExpired:
            proc.kill()
            out, err = proc.communicate()
        return out.decode("utf-8", "replace"), err.decode("utf-8", "replace")


def main() -> int:
    dom, err = run_chrome(["--timeout=25000", "--dump-dom", PAGE.as_uri()], 45)
    errors = [l for l in err.splitlines() if "CONSOLE" in l and "chrome-extension" not in l]
    print("console:", *(errors[:15] or ["(none)"]), sep="\n  ")
    print("dom bytes", len(dom))
    print(" ".join(s + ":" + ("Y" if '<section id="' + s + '"' in dom else "-") for s in SECTIONS))
    counts = {
        "concepts": dom.count('class="concept"'), "steps": dom.count('class="step"'), "classics": dom.count('class="classic"'),
        "adv": dom.count('class="card-d"'), "diagrams": dom.count('class="diagram"'), "lane dots": dom.count('<g class="m"'),
        "mjx": dom.count("<mjx-container"), "chips": len(re.findall(r'class="cchip', dom)), "idrefs": dom.count('class="idref"'), "stages": dom.count('class="stage"'), "glossary rows": dom.count('<td class="en">'),
    }
    print(counts)
    html = PAGE.read_text(encoding="utf-8")
    for spec in sys.argv[1:]:  # e.g. guided:1400x1800[:dark|light] — renders only that section
        parts = spec.split(":")
        anchor, size = parts[0], (parts[1] if len(parts) > 1 else "1400x1600")
        scheme = parts[2] if len(parts) > 2 else ""
        w, _, h = size.partition("x")
        extra_css = "section:not(#%s){display:none!important} .part{display:none!important}" % anchor
        if scheme:
            html_s = html.replace("<title>", '<meta name="color-scheme" content="%s"><title>' % scheme, 1)
        else:
            html_s = html
        dbg = PAGE.parent / f".dbg-{anchor}.html"
        dbg.write_text(html_s.replace("</style>", extra_css + "</style>", 1), encoding="utf-8")
        shot = PAGE.parent / f"shot-{anchor}{'-' + scheme if scheme else ''}.png"
        flags = [f"--window-size={w},{h}", "--hide-scrollbars", "--virtual-time-budget=15000", f"--screenshot={shot}"]
        if scheme == "light":
            flags.append("--blink-settings=preferredColorScheme=1")
        run_chrome(flags + [dbg.as_uri()], 60)
        dbg.unlink(missing_ok=True)
        print("screenshot", shot, shot.exists())
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
