"""Screenshot theme demo pages with headless Chrome (desktop 1400x900, light + dark where applicable)."""
import os, shlex, shutil, signal, subprocess, sys
from concurrent.futures import ThreadPoolExecutor
# CHROME_BIN overrides; otherwise the macOS app, then Chrome / Chromium on PATH. CHROME_ARGS adds flags.
CHROME = os.environ.get("CHROME_BIN") or next(
    (c for c in ["/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"] if os.path.exists(c)), None) or next(
    (shutil.which(c) for c in ["google-chrome", "google-chrome-stable", "chromium", "chromium-browser"] if shutil.which(c)), None)
if not CHROME:
    sys.exit("Chrome not found: set CHROME_BIN")
EXTRA = (["--no-sandbox"] if sys.platform.startswith("linux") and os.geteuid() == 0 else []) + shlex.split(os.environ.get("CHROME_ARGS", ""))
JOBS = [l.split() for l in open(sys.argv[1], encoding="utf-8").read().split("\n") if l.strip()]
def shoot(job):
    name, url = job[0], job[1]
    scheme = {"light": "1", "dark": "0"}[job[2] if len(job) > 2 else "light"]
    out = os.path.abspath(f"shots/{name}.png")
    args = [CHROME, *EXTRA, "--headless=new", "--disable-gpu", "--hide-scrollbars", "--window-size=" + os.environ.get("WS","1400,900") + "",
            "--virtual-time-budget=8000", f"--blink-settings=preferredColorScheme={scheme}", f"--user-data-dir=/tmp/chr-{name}", f"--screenshot={out}", url]
    with open(f"/tmp/chr-{name}.log", "w") as log:
        p = subprocess.Popen(args, stdout=log, stderr=subprocess.STDOUT, start_new_session=True)
        try:
            p.wait(timeout=45)
        except subprocess.TimeoutExpired:
            os.killpg(p.pid, signal.SIGKILL)
    return name, os.path.exists(out) and os.path.getsize(out)
with ThreadPoolExecutor(6) as ex:
    for name, size in ex.map(shoot, JOBS):
        print(name, size)
