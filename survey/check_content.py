"""Compare the visible text of a reference render against the union of all site/ pages.

Usage:
  python3 check_content.py --save .baseline     # dump the current top-level site/*.html pages into .baseline/
  python3 check_content.py .baseline            # compare: reference = union of .baseline/*.html
  python3 check_content.py <reference-dom.html> # compare against a single `--dump-dom` file
Prints text present in the reference but missing from the new pages (should be empty apart from intended wording
changes) and text that is new. TeX is cut out of text nodes, so the result does not depend on whether MathJax loaded.
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

from chrome import chrome_cmd

SITE = Path(__file__).resolve().parent / "site"
SKIP = {"script", "style", "nav", "mjx-container", "title"}
TEX = re.compile(r"\\\((?:.|\n)*?\\\)|\\\[(?:.|\n)*?\\\]")


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
        if self.skip:
            return
        for part in TEX.split(data):
            t = re.sub(r"\s+", " ", part).strip()
            if t:
                self.out.append(t)


def texts(html: str) -> Counter:
    p = TextNodes()
    p.feed(html)
    return Counter(p.out)


def dump(page: Path, attempts: int = 3) -> str:
    """--dump-dom via headless Chrome; Chrome occasionally hangs after printing, so kill it and retry if empty."""
    for _ in range(attempts):
        with tempfile.TemporaryDirectory() as prof, tempfile.TemporaryFile() as sink:
            proc = subprocess.Popen(chrome_cmd("--headless=new", "--disable-gpu", "--no-first-run", "--disable-extensions",
                                     f"--user-data-dir={prof}", "--timeout=20000", "--dump-dom", page.resolve().as_uri()),
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


def site_pages():
    return sorted(p for p in SITE.rglob("*.html") if not p.name.startswith("."))


def main() -> int:
    args = sys.argv[1:]
    if len(args) == 2 and args[0] == "--save":
        out = Path(args[1])
        out.mkdir(parents=True, exist_ok=True)
        for p in sorted(SITE.glob("*.html")):
            (out / p.name).write_text(dump(p), encoding="utf-8")
            print("saved", out / p.name)
        return 0
    if len(args) != 1:
        print(__doc__)
        return 2
    src = Path(args[0])
    ref = Counter()
    for f in (sorted(src.glob("*.html")) if src.is_dir() else [src]):
        ref.update(texts(f.read_text(encoding="utf-8", errors="replace")))
    new = Counter()
    for p in site_pages():
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
