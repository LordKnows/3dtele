"""Compare the visible text of a reference single-page render against the union of all site/ pages.

Usage: python3 check_content.py <reference-dom.html>
The reference is a `--dump-dom` of the old single-page report. Prints text present in the reference but
missing from the new pages (should be empty apart from intended wording changes) and text that is new.
"""
import os
import re
import signal
import subprocess
import sys
import tempfile
from collections import Counter
from html.parser import HTMLParser
from pathlib import Path

CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
SITE = Path(__file__).resolve().parent / "site"
SKIP = {"script", "style", "nav", "mjx-container", "title"}


class TextNodes(HTMLParser):
    def __init__(self):
        super().__init__()
        self.stack, self.skip, self.out = [], 0, []

    def handle_starttag(self, tag, attrs):
        s = tag in SKIP
        self.stack.append(s)
        self.skip += s

    def handle_endtag(self, tag):
        if self.stack:
            self.skip -= self.stack.pop()

    def handle_data(self, data):
        t = re.sub(r"\s+", " ", data).strip()
        if t and not self.skip:
            self.out.append(t)


def texts(html: str) -> Counter:
    p = TextNodes()
    p.feed(html)
    return Counter(p.out)


def dump(page: Path, attempts: int = 3) -> str:
    """--dump-dom via headless Chrome; Chrome occasionally hangs after printing, so kill it and retry if empty."""
    for _ in range(attempts):
        with tempfile.TemporaryDirectory() as prof, tempfile.TemporaryFile() as sink:
            proc = subprocess.Popen([CHROME, "--headless=new", "--disable-gpu", "--no-first-run", "--disable-extensions",
                                     f"--user-data-dir={prof}", "--timeout=20000", "--dump-dom", page.resolve().as_uri()],
                                    stdout=sink, stderr=subprocess.DEVNULL, start_new_session=True)
            try:
                proc.wait(timeout=45)
            except subprocess.TimeoutExpired:
                os.killpg(proc.pid, signal.SIGKILL)
                proc.wait()
            sink.seek(0)
            html = sink.read().decode("utf-8", "replace")
        if "</main>" in html:
            return html
    raise RuntimeError(f"could not render {page}")


def main() -> int:
    ref = texts(Path(sys.argv[1]).read_text(encoding="utf-8", errors="replace"))
    new = Counter()
    for p in sorted(SITE.glob("*.html")):
        new.update(texts(dump(p)))
    missing = {k: v - new.get(k, 0) for k, v in ref.items() if v > new.get(k, 0)}
    added = {k: v - ref.get(k, 0) for k, v in new.items() if v > ref.get(k, 0)}
    print(f"reference text nodes {sum(ref.values())} ({len(ref)} unique); new {sum(new.values())} ({len(new)} unique)")
    print(f"MISSING from new pages: {len(missing)}")
    for k, v in sorted(missing.items(), key=lambda x: -len(x[0])):
        print(f"  - {v}x {k[:200]}")
    print(f"ADDED in new pages: {len(added)}")
    for k, v in sorted(added.items(), key=lambda x: -x[1]):
        print(f"  + {v}x {k[:160]}")
    return 1 if missing else 0


if __name__ == "__main__":
    sys.exit(main())
