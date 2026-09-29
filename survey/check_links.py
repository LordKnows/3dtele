"""Link check for the built site: render every page in headless Chrome and verify

  * every internal href points to an existing file, and its #fragment to an existing element id;
  * every hover-preview entry embedded in a page has a summary and a url that resolves;
  * every old url keeps working: the redirect pages (old top-level pages, the old home's #anchors and
    survey/telepresence-atlas.html) send each old element id to an address that exists, and every content id of
    the old site (from the baseline in .baseline/, when present) has an explicit target.

Usage: python3 check_links.py [--jobs N]
"""
import json
import re
import sys
from concurrent.futures import ThreadPoolExecutor
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urljoin, urlsplit

from check_content import dump

HERE = Path(__file__).resolve().parent
SITE = HERE / "site"
BASELINE = HERE / ".baseline"
OLD_PAGES = ["index.html", "roadmap.html", "foundations.html", "guided.html", "advanced.html", "classics.html",
             "glossary.html", "anchors.html", "landscape.html", "areas.html", "ideas.html"]
# Old element ids that were content anchors (the rest were form controls and SVG markers).
CONTENT_ID = re.compile(r"^(concept|module|walk|guide|adv|classic|stage|area|idea|anchor)-|^(top|summary|sitemap|method|roadmap|"
                        r"roadmap-resources|foundations|guided|advanced|classics|reading|glossary|anchors|map|paradigms|trends|"
                        r"areas|papers|ideas)$")
MAP_RE = re.compile(r"var map = (\{.*?\}), h = ", re.S)


class Scan(HTMLParser):
    def __init__(self):
        super().__init__()
        self.ids, self.hrefs, self.xrefs = set(), [], []

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if a.get("id"):
            self.ids.add(a["id"])
        if tag == "a" and a.get("href") is not None:
            self.hrefs.append(a["href"])
        if a.get("data-xref"):
            self.xrefs.append(a["data-xref"])


def scan(html: str) -> Scan:
    s = Scan()
    s.feed(html)
    return s


def resolve(page: str, href: str):
    """Site-relative (path, fragment) for an internal href on `page`; None for external links."""
    if re.match(r"^[a-z][a-z0-9+.-]*:", href, re.I):
        return None
    u = urlsplit(urljoin("https://site.invalid/" + page, href))
    path = u.path.lstrip("/") or "index.html"
    if path.endswith("/"):
        path += "index.html"
    return path, u.fragment


def main() -> int:
    args = sys.argv[1:]
    jobs = int(args[args.index("--jobs") + 1]) if "--jobs" in args else 6
    redirects = {p for p in OLD_PAGES if p != "index.html"}
    pages = sorted(p.relative_to(SITE).as_posix() for p in SITE.rglob("*.html") if not p.name.startswith("."))
    rendered = [p for p in pages if p not in redirects]
    errors, warnings = [], []

    def render(p):
        try:
            return p, scan(dump(SITE / p))
        except RuntimeError as e:
            return p, e
    with ThreadPoolExecutor(max_workers=jobs) as ex:
        dom = dict(ex.map(render, rendered))
    for p, s in dom.items():
        if isinstance(s, Exception):
            errors.append(f"{p}: {s}")
    dom = {p: s for p, s in dom.items() if not isinstance(s, Exception)}

    def check_target(where, path, frag):
        if not (SITE / path).is_file():
            errors.append(f"{where}: no file {path}")
        elif frag and path in dom and frag not in dom[path].ids:
            errors.append(f"{where}: no #{frag} in {path}")
        elif frag and path not in dom:
            errors.append(f"{where}: #{frag} points into unrendered page {path}")

    n_links = 0
    for p, s in dom.items():
        for href in s.hrefs:
            r = resolve(p, href)
            if r is None:
                continue
            n_links += 1
            check_target(f"{p} href={href}", *r)
        # Hover previews: the entries this page embeds.
        src = (SITE / p).read_text(encoding="utf-8")
        m = re.search(r'id="data">(.*?)</script>', src, re.S)
        xref = json.loads(m.group(1)).get("xref", {}) if m else {}
        for k, x in xref.items():
            if not str(x.get("s", "")).strip():
                errors.append(f"{p}: preview {k} has no summary")
            check_target(f"{p} preview {k}", *resolve("", x["u"]))
        for k in set(s.xrefs) - set(xref):
            errors.append(f"{p}: link to {k} has no preview entry")

    # Old urls: redirect pages, the new home's old #anchors, and the old single-page report.
    maps = {}
    for old in OLD_PAGES:
        m = MAP_RE.search((SITE / old).read_text(encoding="utf-8"))
        if not m:
            errors.append(f"{old}: no redirect map")
            continue
        maps[old] = json.loads(m.group(1))
    for old, mp in maps.items():
        for k, u in mp.items():
            check_target(f"{old}#{k}", *resolve("", u))
    atlas = MAP_RE.search((HERE / "telepresence-atlas.html").read_text(encoding="utf-8"))
    if atlas:
        for k, u in json.loads(atlas.group(1)).items():
            check_target(f"telepresence-atlas.html#{k}", *resolve("", u))
    else:
        errors.append("telepresence-atlas.html: no redirect map")
    n_old = 0
    if BASELINE.is_dir():
        for old in OLD_PAGES:
            f = BASELINE / old
            if not f.exists():
                continue
            for i in sorted(scan(f.read_text(encoding="utf-8", errors="replace")).ids):
                if not CONTENT_ID.search(i):
                    continue
                n_old += 1
                if i not in maps.get(old, {}) and not (old == "index.html" and i == "top"):
                    errors.append(f"old {old}#{i}: no redirect target")
    else:
        warnings.append("no .baseline/ directory: old anchors not checked against the old site")

    print(f"pages {len(pages)} (rendered {len(dom)}, redirects {len(redirects)}); internal links {n_links}; "
          f"old anchors checked {n_old}; errors {len(errors)}")
    for w in warnings:
        print("  warning:", w)
    for e in errors[:80]:
        print("  -", e)
    if len(errors) > 80:
        print(f"  ... {len(errors) - 80} more")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
