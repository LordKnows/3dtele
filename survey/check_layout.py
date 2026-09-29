"""Layout checks in real 390px (phone) and 1400px (desktop) viewports, using an iframe in headless Chrome.

For every page: horizontal overflow with every <details> expanded, and reference lists whose items do not line up. For a set of deep links: where the target
lands relative to the viewport top (should clear the sticky bar on phones and sit near the top on desktop).
Each measurement runs in its own short Chrome process; several run in parallel.
"""
import json
import os
import re
import signal
import subprocess
import sys
import tempfile
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from chrome import chrome_cmd

SITE = Path(__file__).resolve().parent / "site"
WIDTHS = [390, 1400]
DEEP_LINKS = ["foundations.html#concept-g-pinhole", "guided.html#walk-ha-h3", "classics.html#classic-40",
              "roadmap.html#stage-2", "areas.html#area-avatars", "advanced.html#adv-a-geo-fm", "ideas.html#idea-C02",
              "basics/foundations/g-epipolar.html#cases", "works/walkthrough/quark.html#walk-quark-q7",
              "basics/classics/t-ibr-geometry.html#classic-1", "basics/glossary.html#term-homogeneous-coordinates",
              "works/field-map.html#paradigms", "overview/how-to-use.html#method"]
# The first seven are old urls: they go through the redirect pages to the new pages.
NOTE_PAGES = ["basics/foundations/g-epipolar.html", "works/walkthrough/quark.html", "basics/classics/t-ibr-geometry.html"]

HARNESS = """<!doctype html><html><head><meta charset="utf-8"></head><body style="margin:0"><pre id="out">running</pre>
<script>
var job = %(job)s;
var f = document.createElement("iframe");
f.style.width = job.w + "px"; f.style.height = "900px"; f.style.border = "0";
f.onload = function () {
  setTimeout(function () {
    var d = f.contentDocument, de = d.documentElement, res = { job: job };
    if (job.kind === "overflow") {
      d.querySelectorAll("details").forEach(function (x) { x.open = true; });
      setTimeout(function () {
        res.scrollWidth = de.scrollWidth; res.clientWidth = de.clientWidth; res.culprits = [];
        // Reference lists: the text column of every item starts at the same x.
        res.misaligned = [];
        d.querySelectorAll("ul.refs").forEach(function (ul) {
          var xs = Array.prototype.map.call(ul.children, function (li) { return li.lastElementChild ? li.lastElementChild.getBoundingClientRect().left : null; })
            .filter(function (x) { return x !== null; });
          if (xs.length > 1 && Math.max.apply(null, xs) - Math.min.apply(null, xs) > 1) {
            var where = ul.closest("[id]");
            res.misaligned.push("#" + (where ? where.id : "") + " spread=" + Math.round(Math.max.apply(null, xs) - Math.min.apply(null, xs)) + "px");
          }
        });
        if (de.scrollWidth > de.clientWidth + 1) {
          var hits = [];
          var inScroller = function (n) {
            for (var q = n.parentElement; q && q !== d.body; q = q.parentElement) {
              var ox = f.contentWindow.getComputedStyle(q).overflowX;
              if (ox === "auto" || ox === "scroll" || ox === "hidden") return true;
            }
            return false;
          };
          d.querySelectorAll("body *").forEach(function (n) {
            var r = n.getBoundingClientRect();
            if (r.right > de.clientWidth + 2 && !inScroller(n)) {
              var p = n.parentElement, where = n.closest("[id]");
              hits.push({ r: Math.round(r.right), s: n.tagName + "." + (typeof n.className === "string" ? n.className.split(" ")[0] : "") + " < " + (p ? p.tagName + "." + (typeof p.className === "string" ? p.className.split(" ")[0] : "") : "") + " @#" + (where ? where.id : "") + " [" + (n.textContent || "").trim().slice(0, 40) + "]" });
            }
          });
          hits.sort(function (a, b) { return b.r - a.r; });
          res.culprits = hits.slice(0, 5).map(function (h) { return h.s + " right=" + h.r; });
        }
        document.getElementById("out").textContent = JSON.stringify(res);
      }, 800);
    } else if (job.kind === "notes") {
      // Phones: side / margin notes are folded behind a toggle that opens them.
      var sn = d.querySelector(".sidenote, .marginnote"), win = f.contentWindow;
      var lab = sn ? sn.parentElement.querySelector("label.margin-toggle") : null;
      res.folded = sn ? win.getComputedStyle(sn).display === "none" : null;
      res.toggle = lab ? win.getComputedStyle(lab).display !== "none" : null;
      if (lab) lab.click();
      res.opens = sn ? win.getComputedStyle(sn).display !== "none" : null;
      document.getElementById("out").textContent = JSON.stringify(res);
    } else if (job.kind === "menu") {
      // Dropdowns work from the keyboard: open, arrow into the list, Escape closes and returns focus.
      var btn = d.querySelector(".menu-btn"), drop = btn && btn.parentElement.querySelector(".drop"), w2 = f.contentWindow;
      btn.focus(); btn.click();
      res.opens = btn.getAttribute("aria-expanded") === "true" && w2.getComputedStyle(drop).display !== "none";
      btn.dispatchEvent(new KeyboardEvent("keydown", { key: "ArrowDown", bubbles: true }));
      res.arrow = d.activeElement === drop.querySelector("a");
      d.activeElement.dispatchEvent(new KeyboardEvent("keydown", { key: "Escape", bubbles: true }));
      res.escape = btn.getAttribute("aria-expanded") === "false" && d.activeElement === btn && w2.getComputedStyle(drop).display === "none";
      document.getElementById("out").textContent = JSON.stringify(res);
    } else {
      var id = job.src.split("#")[1], t = d.getElementById(id), bar = d.querySelector("nav.toc");
      res.top = t ? Math.round(t.getBoundingClientRect().top) : null;
      res.open = t && t.tagName === "DETAILS" ? t.open : null;
      res.barBottom = job.w < 1001 && bar ? Math.round(bar.getBoundingClientRect().bottom) : 0;
      document.getElementById("out").textContent = JSON.stringify(res);
    }
  }, 4000);
};
f.src = job.src; document.body.appendChild(f);
</script></body></html>"""


def measure(job):
    with tempfile.TemporaryDirectory() as tmp:
        # The harness must be same-origin with the page: put it in site/ under a unique name.
        harness = SITE / f".layout-{os.getpid()}-{abs(hash(json.dumps(job))) % 10**8}.html"
        harness.write_text(HARNESS % {"job": json.dumps(job)}, encoding="utf-8")
        try:
            with tempfile.TemporaryFile() as sink:
                proc = subprocess.Popen(chrome_cmd("--headless=new", "--disable-gpu", "--no-first-run", "--disable-extensions",
                                         "--allow-file-access-from-files", f"--user-data-dir={tmp}", "--window-size=1500,1000",
                                         "--virtual-time-budget=30000", "--dump-dom", harness.as_uri()),
                                        stdout=sink, stderr=subprocess.DEVNULL, start_new_session=True)
                try:
                    proc.wait(timeout=120)
                except subprocess.TimeoutExpired:
                    os.killpg(proc.pid, signal.SIGKILL)
                    proc.wait()
                sink.seek(0)
                out = sink.read().decode("utf-8", "replace")
        finally:
            harness.unlink(missing_ok=True)
    m = re.search(r'<pre id="out">(\{.*?\})</pre>', out, re.S)
    if not m:
        return {"job": job, "error": "no result"}
    return json.loads(m.group(1).replace("&quot;", '"').replace("&amp;", "&").replace("&lt;", "<").replace("&gt;", ">"))


def main() -> int:
    pages = sorted(p for p in SITE.rglob("*.html") if not p.name.startswith("."))
    jobs = [{"kind": "overflow", "w": w, "src": p.relative_to(SITE).as_posix()} for w in WIDTHS for p in pages]
    jobs += [{"kind": "jump", "w": w, "src": l} for w in WIDTHS for l in DEEP_LINKS]
    jobs += [{"kind": "notes", "w": 390, "src": s} for s in NOTE_PAGES]
    jobs += [{"kind": "menu", "w": 1400, "src": s} for s in ("index.html", "basics/foundations/g-epipolar.html")]
    with ThreadPoolExecutor(max_workers=4) as ex:
        results = list(ex.map(measure, jobs))
    bad = 0
    for r in results:
        j = r["job"]
        if "error" in r:
            bad += 1
            print(f"FAIL {j['kind']:8s} {j['w']:4d}px {j['src']:36s} {r['error']}")
        elif j["kind"] in ("notes", "menu"):
            keys = ("folded", "toggle", "opens") if j["kind"] == "notes" else ("opens", "arrow", "escape")
            ok = all(r.get(k) is True for k in keys)
            bad += not ok
            print(f"{'ok  ' if ok else 'FAIL'} {j['kind']:8s} {j['w']:4d}px {j['src']:36s} " + " ".join(f"{k}={r.get(k)}" for k in keys))
        elif j["kind"] == "overflow":
            ok = r["scrollWidth"] <= r["clientWidth"] + 1 and not r.get("misaligned")
            bad += not ok
            print(f"{'ok  ' if ok else 'FAIL'} overflow {j['w']:4d}px {j['src']:36s} scrollWidth={r['scrollWidth']} client={r['clientWidth']} "
                  f"{'' if ok else (r['culprits'] or '') + ' misaligned lists: ' + str(r.get('misaligned', [])[:3])}")
        else:
            want = r["barBottom"]
            ok = r["top"] is not None and want <= r["top"] <= want + 60 and r["open"] is not False
            bad += not ok
            print(f"{'ok  ' if ok else 'FAIL'} jump     {j['w']:4d}px {j['src']:36s} top={r['top']} bar_bottom={want} open={r['open']}")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
