"""Assemble survey, idea-review and learning data, validate cross-links, and render the multi-page site into site/."""
import html
import json
import re
import sys
from pathlib import Path

import routes
import wording

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data"


def load_json(p: Path):
    with p.open(encoding="utf-8") as f:
        return json.load(f)


def paper_key(w: dict) -> str:
    url = (w.get("url") or "").strip().lower()
    m = re.search(r"arxiv\.org/(?:abs|html|pdf)/(\d{4}\.\d{4,5})", url)
    if m:
        return "arxiv:" + m.group(1)
    t = re.sub(r"[^a-z0-9]+", "", (w.get("title") or "").lower())
    return "title:" + t[:80]


TIER_RANK = {"milestone": 0, "important": 1, "relevant": 2}


def to_year(v):
    try:
        return int(str(v)[:4])
    except (TypeError, ValueError):
        return None


def build_survey():
    survey = load_json(DATA / "survey.json")
    # Deep reads beyond the two in survey.json live one per file (data/anchor_<key>.json).
    anchors = survey.setdefault("anchors", {})
    for p in load_json(DATA / "site" / "papers.json")["papers"]:
        f = DATA / f"anchor_{p['key']}.json"
        if p["key"] not in anchors and f.exists():
            anchors[p["key"]] = load_json(f)
    areas = survey["areas"]
    papers: dict[str, dict] = {}
    for a in areas:
        for w in a.get("works", []):
            if not isinstance(w, dict) or not w.get("title"):
                continue
            k = paper_key(w)
            rec = papers.get(k)
            if rec is None:
                papers[k] = {
                    "title": w["title"], "authors": w.get("authors", ""), "year": to_year(w.get("year")),
                    "venue": w.get("venue", ""), "url": w.get("url", ""), "summary_zh": w.get("summary_zh", ""),
                    "key_numbers": w.get("key_numbers", ""), "tier": w.get("tier", "relevant"), "areas": [a["key"]],
                }
                continue
            if a["key"] not in rec["areas"]:
                rec["areas"].append(a["key"])
            if TIER_RANK.get(w.get("tier"), 2) < TIER_RANK.get(rec["tier"], 2):
                rec["tier"] = w["tier"]
            for f in ("summary_zh", "key_numbers"):
                if len(w.get(f, "")) > len(rec[f]):
                    rec[f] = w[f]
    area_out = [{k: v for k, v in a.items() if k != "works"} for a in areas]
    return survey, area_out, list(papers.values())


def build_ideas():
    review = load_json(DATA / "review.json")
    ideas_zh = {x["id"]: x for x in load_json(DATA / "ideas_zh.json")}
    ideas = []
    for r in review:
        rv, nv = r["review"], r["novelty"]
        zh = ideas_zh[r["id"]]
        ideas.append({
            "id": r["id"], "name": r["name"], "decision": rv["decision"], "scores": rv["scores"],
            "sharpened": zh["sharpened"], "experiments": zh["experiments"],
            "first_two_week_test": zh["first_two_week_test"], "kill_criteria": zh["kill_criteria"],
            "reviewer_objections": zh["reviewer_objections"], "synergies": zh["synergies"],
            "effort": zh["effort"], "venue": zh["venue"],
            "novelty": {"verdict": nv["verdict"], "remaining_novel_angle": zh["remaining_novel_angle"], "threats": zh["threats"]},
        })
    ideas.sort(key=lambda x: (-x["scores"]["overall"], -(x["scores"]["novelty"] + x["scores"]["significance"]), x["id"]))
    return ideas


class Links:
    """Tracks invalid cross-link ids so they can be reported and dropped."""

    def __init__(self, concept_ids, adv_ids):
        self.concepts, self.adv, self.bad = set(concept_ids), set(adv_ids), []

    def c(self, ids, where):
        out = []
        for i in ids or []:
            if i in self.concepts:
                if i not in out:
                    out.append(i)
            else:
                self.bad.append(f"{where}: concept {i!r}")
        return out

    def a(self, ids, where):
        out = []
        for i in ids or []:
            if i in self.adv:
                if i not in out:
                    out.append(i)
            else:
                self.bad.append(f"{where}: advanced {i!r}")
        return out


def build_learn(stats: dict):
    sk = load_json(DATA / "learn" / "skeleton.json")
    content_path = DATA / "learn" / "content.json"
    if not content_path.exists():
        print("no learning content yet; building without it", file=sys.stderr)
        return {}
    c = load_json(content_path)
    concept_ids = [x["id"] for m in sk["modules"] for x in m["concepts"]]
    adv_ids = [t["id"] for t in sk["advanced_topics"]]
    lk = Links(concept_ids, adv_ids)

    # Foundations: keep skeleton order and titles, take reviewed content.
    by_mod = {m["module_id"]: m for m in c.get("foundations") or [] if m}
    modules = []
    fixes_found = 0
    for m in sk["modules"]:
        got = by_mod.get(m["id"])
        if got is None:
            print(f"missing module {m['id']}", file=sys.stderr)
            continue
        fixes_found += len(got.get("change_log") or [])
        by_c = {x["id"]: x for x in got.get("concepts", [])}
        concepts = []
        for sc in m["concepts"]:
            x = by_c.get(sc["id"])
            if x is None:
                print(f"missing concept {sc['id']}", file=sys.stderr)
                continue
            x = dict(x)
            x["prereqs"] = lk.c(x.get("prereqs") or sc["prereqs"], f"prereq of {sc['id']}")
            concepts.append(x)
        extra = [k for k in by_c if k not in {s["id"] for s in m["concepts"]}]
        if extra:
            print(f"module {m['id']}: dropping unknown concepts {extra}", file=sys.stderr)
        modules.append({"id": m["id"], "title_zh": m["title_zh"], "title_en": m["title_en"], "goal_zh": m["goal_zh"],
                        "intro_zh": got.get("intro_zh", ""), "study_tips_zh": got.get("study_tips_zh", ""), "concepts": concepts})
    stats["foundation_fixes"] = fixes_found

    # Advanced topics in skeleton order.
    topics = {}
    adv_fixes = 0
    for g in c.get("advanced") or []:
        if not g:
            continue
        adv_fixes += len(g.get("change_log") or [])
        for t in g.get("topics", []):
            topics[t["id"]] = t
    advanced = []
    for st in sk["advanced_topics"]:
        t = topics.get(st["id"])
        if t is None:
            print(f"missing advanced topic {st['id']}", file=sys.stderr)
            continue
        t = dict(t)
        t["prereqs"] = lk.c(t.get("prereqs") or st["prereqs"], f"prereq of {st['id']}")
        advanced.append(t)
    stats["advanced_fixes"] = adv_fixes

    # Classics: drop removed / 2026+.
    theme_ids = {t["id"] for t in sk["classic_themes"]}
    classics, removed, corrected = [], 0, 0
    for p in c.get("classics") or []:
        if p.get("status") == "removed":
            removed += 1
            continue
        if p.get("status") == "corrected":
            corrected += 1
        yr = to_year(p.get("year"))
        if yr is None or yr > 2025:
            removed += 1
            continue
        themes = [t for t in (p.get("themes") or [p.get("theme")]) if t in theme_ids]
        if not themes:
            themes = [p.get("theme")] if p.get("theme") in theme_ids else []
        classics.append({
            "title": p["title"], "authors": p.get("authors", ""), "year": yr, "venue": p.get("venue", ""), "url": p.get("url", ""),
            "citations": p.get("citations", -1), "citations_source": p.get("citations_source", ""),
            "theme": themes[0] if themes else "", "themes": themes,
            "influence_zh": p.get("influence_zh", ""), "contributions_zh": p.get("contributions_zh", ""),
            "anchor_link_zh": p.get("anchor_link_zh", ""),
            "concept_ids": lk.c([i for i in p.get("concept_ids") or [] if not str(i).startswith("a-")], f"classic {p['title'][:30]}"),
            "adv_ids": lk.a([i for i in p.get("concept_ids") or [] if str(i).startswith("a-")], f"classic {p['title'][:30]}"),
            "difficulty": p.get("difficulty", ""), "must_read": bool(p.get("must_read")),
        })
    classics.sort(key=lambda p: (p["year"], -(p["citations"] or 0)))
    stats.update(classics_removed=removed, classics_corrected=corrected)

    # Guided walkthroughs.
    # Quark and Ha et al. were checked against the paper text; the later deep reads against code and search results.
    guided, guide_fixes, new_fixes = {}, 0, 0
    for g in c.get("guided") or []:
        if not g:
            continue
        if g["anchor"] in routes.LEGACY_PAPERS:
            guide_fixes += len(g.get("fixes") or [])
        else:
            new_fixes += len(g.get("fixes") or [])
        g = {k: v for k, v in g.items() if k != "fixes"}
        g["before_you_read"] = [b for b in g.get("before_you_read", []) if lk.c([b.get("concept_id")], f"guide {g['anchor']} before")]
        for s in g.get("walkthrough", []):
            ids = s.get("concept_ids") or []
            s["concept_ids"] = lk.c([i for i in ids if not str(i).startswith("a-")], f"guide {g['anchor']} {s.get('id')}")
            s["adv_ids"] = lk.a([i for i in ids if str(i).startswith("a-")], f"guide {g['anchor']} {s.get('id')}")
        for x in g.get("exercises", []):
            ids = x.get("concept_ids") or []
            x["concept_ids"] = lk.c([i for i in ids if not str(i).startswith("a-")], f"guide {g['anchor']} exercise")
            x["adv_ids"] = lk.a([i for i in ids if str(i).startswith("a-")], f"guide {g['anchor']} exercise")
        guided[g["anchor"]] = g
    stats.update(guide_fixes=guide_fixes, new_fixes=new_fixes)

    roadmap = c.get("roadmap") or {}
    for s in roadmap.get("stages", []):
        s["concept_ids"] = lk.c(s.get("concept_ids"), f"roadmap {s.get('id')}")
        s["advanced_ids"] = lk.a(s.get("advanced_ids"), f"roadmap {s.get('id')}")

    seen, glossary = set(), []
    for t in (c.get("glossary") or {}).get("terms", []):
        k = (t.get("term_en") or "").strip().lower()
        if not k or k in seen:
            continue
        seen.add(k)
        t = dict(t)
        t["concept_id"] = t["concept_id"] if t.get("concept_id") in lk.concepts else ""
        glossary.append(t)

    if lk.bad:
        print(f"dropped {len(lk.bad)} invalid cross-links, e.g. {lk.bad[:5]}", file=sys.stderr)
    stats.update(concepts=sum(len(m["concepts"]) for m in modules), advanced=len(advanced), classics=len(classics),
                 glossary=len(glossary), steps=sum(len(g.get("walkthrough", [])) for k, g in guided.items() if k in routes.LEGACY_PAPERS),
                 steps_new=sum(len(g.get("walkthrough", [])) for k, g in guided.items() if k not in routes.LEGACY_PAPERS),
                 deepreads_new=sum(1 for k in guided if k not in routes.LEGACY_PAPERS))
    return {"modules": modules, "advanced": advanced, "classics": classics, "guided": guided,
            "roadmap": roadmap, "glossary": glossary, "themes": sk["classic_themes"]}


# ---------- site ----------
SRC, SITE_DIR = ROOT / "src", ROOT / "site"
TUFTE = SRC / "tufte"
SAFE_URL = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._/-]*(\?[A-Za-z0-9=&._-]+)?(#[A-Za-z0-9._-]+)?$")


def reverse_index(learn):
    """Concept -> guided steps / classics / advanced topics that reference it (shown on concept cards)."""
    walk_by, classic_by, adv_by = {}, {}, {}
    for anchor, g in (learn.get("guided") or {}).items():
        for s in g.get("walkthrough", []):
            for c in s.get("concept_ids", []):
                walk_by.setdefault(c, []).append({"anchor": anchor, "id": s.get("id"), "title": s.get("title_zh", "")})
    for i, p in enumerate(learn.get("classics", [])):
        for c in p.get("concept_ids", []):
            classic_by.setdefault(c, []).append({"i": i, "title": p.get("title", "")})
    for t in learn.get("advanced", []):
        for c in t.get("prereqs", []):
            adv_by.setdefault(c, []).append(t["id"])
    return {"walkBy": walk_by, "classicBy": classic_by, "advBy": adv_by}


def concept_routes(learn, rev, xref, minutes) -> list:
    order = [(m, c) for m in learn.get("modules", []) for c in m["concepts"]]
    out = []
    for i, (m, c) in enumerate(order):
        prev = f"concept-{order[i - 1][1]['id']}" if i > 0 else None
        nxt = f"concept-{order[i + 1][1]['id']}" if i + 1 < len(order) else None
        walk = [f"walk-{w['anchor']}-{w['id']}" for w in rev["walkBy"].get(c["id"], [])]
        classics = [f"classic-{x['i']}" for x in rev["classicBy"].get(c["id"], [])]
        adv = [f"adv-{a}" for a in rev["advBy"].get(c["id"], [])]
        refs = ({f"concept-{p}" for p in c.get("prereqs", [])} | routes.ids_in(c, xref) | {f"module-{m['id']}"}
                | set(walk) | set(classics) | set(adv) | {k for k in (prev, nxt) if k})
        out.append({
            "path": xref[f"concept-{c['id']}"]["u"], "template": "concept", "scripts": [], "nav": "basics",
            "navItem": "basics/foundations/index.html", "title": c["name_zh"], "description": routes.first_sentence(c.get("tldr_zh"), 120),
            "crumbs": [["Basics", ""], ["Foundations", "basics/foundations/index.html"],
                       [f"{m['id']} {m['title_zh']}", xref[f"module-{m['id']}"]["u"]]],
            "data": {"concept": c, "module": f"module-{m['id']}", "walk": walk, "classics": classics, "adv": adv,
                     "prev": prev, "next": nxt, "readMin": minutes[c["id"]]},
            "refs": refs, "head_extra": "",
        })
    return out


def render_article(route, t, meta, xref) -> str:
    """One page of the redesigned site: shell + inlined CSS/JS + the page's data (only the xref entries it links to)."""
    root = "../" * route["path"].count("/")
    data = {"site": {"brand": routes.BRAND, "root": root, "path": route["path"], "nav": routes.NAV, "navCur": route["nav"],
                     "navItem": route["navItem"], "crumbs": route["crumbs"], "date": meta.get("date", "")},
            "xref": {k: xref[k] for k in sorted(route["refs"]) if k in xref}}
    missing = sorted(k for k in route["refs"] if k not in xref)
    if missing:
        print(f"{route['path']}: no link target for {missing}", file=sys.stderr)
    bad = sorted({x["u"] for x in data["xref"].values() if not SAFE_URL.match(x["u"])})
    if bad:
        raise ValueError(f"{route['path']}: unsafe urls {bad}")
    if route["template"] == "concept":
        data.update(route["data"])
    else:
        data["page"] = route["page"]
        data.update(route.get("extra", {}))
    blob = json.dumps(data, ensure_ascii=False).replace("</", "<\\/").replace("<!--", "<\\u0021--")
    scripts = [t["lib"], t["frame"]] + [(TUFTE / s).read_text(encoding="utf-8") for s in route["scripts"]]
    scripts += [(TUFTE / f"{route['template']}.js").read_text(encoding="utf-8"), "  finishPage();"]
    title = f"{route['title']} · {routes.BRAND}" if route["title"] else routes.BRAND
    out = t["shell"]
    for k, v in (("{{TITLE}}", html.escape(title)), ("{{DESCRIPTION}}", html.escape(route["description"], quote=True)),
                 ("{{HEAD}}", route.get("head_extra", "")), ("{{STYLE}}", t["css"].replace("{{ROOT}}", root)),
                 ("{{SCRIPT}}", "\n".join(scripts)), ("{{DATA}}", blob)):
        out = out.replace(k, v, 1)
    return out


def redirect_script(mapping: dict, prefix: str, fallback: bool) -> str:
    """Inline script sending an old #anchor to its new url (relative to `prefix`); without a match it goes to the
    page default when `fallback` is set."""
    cfg = json.dumps(mapping, ensure_ascii=False, sort_keys=True).replace("</", "<\\/")
    default = 'map[""]' if fallback else "null"
    return f"""<script>
(function () {{
  var map = {cfg}, h = location.hash ? location.hash.slice(1) : "";
  if (!/^[A-Za-z0-9._~-]*$/.test(h)) h = "";
  var to = Object.prototype.hasOwnProperty.call(map, h) && h ? map[h] : {default};
  if (to) location.replace({json.dumps(prefix)} + to);
}})();
</script>"""


def write_redirects(legacy: dict):
    """The old top-level pages become redirect pages; the old single-page report at survey/telepresence-atlas.html too."""
    for old, mapping in legacy.items():
        if old == "index.html":
            continue
        target = html.escape(mapping[""], quote=True)
        (SITE_DIR / old).write_text(f"""<!doctype html>
<html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex"><title>{routes.BRAND}</title>
{redirect_script(mapping, "", True)}
</head><body><p>本页已改版，请前往 <a href="{target}">{target}</a>。</p></body></html>
""", encoding="utf-8")
    everything = {k: v for m in legacy.values() for k, v in m.items() if k}
    everything[""] = "index.html"
    (ROOT / "telepresence-atlas.html").write_text(f"""<!doctype html>
<html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex"><title>{routes.BRAND}</title>
{redirect_script(everything, "site/", True)}
</head><body><p>{routes.BRAND} 已改版为多页网站，请打开 <a href="site/index.html">site/index.html</a>。</p></body></html>
""", encoding="utf-8")


def write_artifact_entry(index_html: str):
    """claude.ai Artifacts wrap the published page in their own <!doctype>/<head>/<body> skeleton, so the entry
    page must be a fragment (title first). The full pages in site/ are uploaded next to it as supporting files."""
    body = re.sub(r"<!doctype html>\s*|</?html[^>]*>\s*|</?head>\s*|</?body>\s*", "", index_html, flags=re.I)
    body = re.sub(r'<meta (charset|name="viewport")[^>]*>\s*', "", body)
    out = ROOT / ".artifact" / "index.html"
    out.parent.mkdir(exist_ok=True)
    out.write_text(body, encoding="utf-8")


def main() -> int:
    survey, areas, papers = build_survey()
    ideas = build_ideas()
    stats: dict = {}
    learn = build_learn(stats)
    meta = load_json(ROOT / "meta.json")
    if stats:
        meta["method_zh"] = meta["method_zh"] + "\n\n" + meta.get("learn_method_zh", "").format(**stats)

    # Display-layer wording (docs/redesign-tufte.md 5.1); the data files keep their original text.
    survey, areas, papers, ideas, learn, meta = (wording.apply_all(x) for x in (survey, areas, papers, ideas, learn, meta))
    mods = learn.get("modules", [])
    counts = {"concepts": sum(len(m["concepts"]) for m in mods), "advanced": len(learn.get("advanced", [])),
              "classics": len(learn.get("classics", [])), "papers": len(papers), "ideas": len(ideas),
              "glossary": len(learn.get("glossary", [])), "areas": len(areas),
              "stages": len((learn.get("roadmap") or {}).get("stages", [])),
              "steps": {k: len(g.get("walkthrough", [])) for k, g in (learn.get("guided") or {}).items()}}
    synth = survey.get("synth") or {}
    overview = load_json(DATA / "site" / "overview.json")
    fields = {"stages": counts["stages"], "modules": len(mods), "concepts": counts["concepts"], "advanced": counts["advanced"],
              "classics": counts["classics"], "glossary": counts["glossary"], "papers": counts["papers"], "areas": counts["areas"],
              "ideas": counts["ideas"], "layers": len(synth.get("field_map", [])), "steps_quark": counts["steps"].get("quark", 0),
              "steps_ha": counts["steps"].get("ha", 0), "deepreads": len(counts["steps"]),
              "steps_all": sum(counts["steps"].values()),
              "techniques": sum(len(g["items"]) for g in overview["methodology"]["groups"])}
    page_desc = {k: v.format(**fields) for k, v in overview["page_desc"].items()}
    page_desc = wording.apply_all(page_desc)
    section_title = {"top": routes.BRAND, "methodology": "领域重要技术总览", "howto": "如何使用本站", "roadmap": "学习路线",
                     "foundations": "基础知识", "advanced": "进阶专题", "classics": "经典论文", "glossary": "术语表",
                     "anchors": "论文精读与论文库", "guided": "精读导读", "map": "领域全景", "areas": "子方向",
                     "ideas": "研究方向", "trends": "趋势与挑战"}
    minutes = {c["id"]: routes.read_minutes(c) for m in mods for c in m["concepts"]}
    registry = load_json(DATA / "site" / "papers.json")
    ctx = {"learn": learn, "survey": survey, "areas": areas, "papers": papers, "ideas": ideas, "meta": meta, "overview": overview,
           "counts": counts, "page_desc": page_desc, "section_title": section_title, "minutes": minutes, "registry": registry}
    xref = routes.xref_table(ctx)
    legacy = routes.legacy_map(xref)
    home_legacy = {k: v for k, v in legacy["index.html"].items() if k and k != "top"}
    all_routes = concept_routes(learn, reverse_index(learn), xref, minutes) + routes.site_routes(ctx, xref, redirect_script(home_legacy, "", False))
    paths = [r["path"] for r in all_routes]
    dup = sorted({p for p in paths if paths.count(p) > 1})
    if dup:
        raise ValueError(f"duplicate routes {dup}")

    t = {k: (TUFTE / f).read_text(encoding="utf-8") for k, f in (("shell", "shell.html"), ("css", "tufte.css"), ("frame", "frame.js"))}
    t["lib"] = (SRC / "lib.js").read_text(encoding="utf-8")
    SITE_DIR.mkdir(exist_ok=True)
    total, biggest = 0, []
    for route in all_routes:
        out = SITE_DIR / route["path"]
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(render_article(route, t, meta, xref), encoding="utf-8")
        json.loads(re.search(r'id="data">(.*?)</script>', out.read_text(encoding="utf-8"), re.S).group(1))
        size = out.stat().st_size
        total += size
        biggest.append((size, route["path"]))
    write_redirects(legacy)
    write_artifact_entry((SITE_DIR / "index.html").read_text(encoding="utf-8"))
    biggest.sort(reverse=True)
    print("largest: " + ", ".join(f"{p} {s / 1024:.0f} KB" for s, p in biggest[:4]))
    print(f"site/: {len(all_routes)} pages + {len(legacy) - 1} redirects, {total / 1024 / 1024:.1f} MB total; stats={stats}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
