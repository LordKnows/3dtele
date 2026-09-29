"""Assemble survey, idea-review and learning data, validate cross-links, and render the multi-page site into site/."""
import html
import json
import re
import sys
from pathlib import Path

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
    guided, guide_fixes = {}, 0
    for g in c.get("guided") or []:
        if not g:
            continue
        guide_fixes += len(g.get("fixes") or [])
        g = {k: v for k, v in g.items() if k != "fixes"}
        g["before_you_read"] = [b for b in g.get("before_you_read", []) if lk.c([b.get("concept_id")], f"guide {g['anchor']} before")]
        for s in g.get("walkthrough", []):
            ids = s.get("concept_ids") or []
            s["concept_ids"] = lk.c([i for i in ids if not str(i).startswith("a-")], f"guide {g['anchor']} {s.get('id')}")
            s["adv_ids"] = lk.a([i for i in ids if str(i).startswith("a-")], f"guide {g['anchor']} {s.get('id')}")
        for x in g.get("exercises", []):
            x["concept_ids"] = lk.c(x.get("concept_ids"), f"guide {g['anchor']} exercise")
        guided[g["anchor"]] = g
    stats["guide_fixes"] = guide_fixes

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
                 glossary=len(glossary), steps=sum(len(g.get("walkthrough", [])) for g in guided.values()))
    return {"modules": modules, "advanced": advanced, "classics": classics, "guided": guided,
            "roadmap": roadmap, "glossary": glossary, "themes": sk["classic_themes"]}


# ---------- site structure ----------
# One entry per page, in reading order. "sections" are the top-level section ids rendered on that page
# (used for cross-page links); "script" is the page component in src/pages/.
PAGES = [
    {"key": "home", "file": "index.html", "label": "概览", "group": None, "script": "home.js",
     "sections": ["top", "summary", "sitemap", "method"]},
    {"key": "roadmap", "file": "roadmap.html", "label": "学习路线", "group": "入门学习", "script": "roadmap.js",
     "sections": ["roadmap", "roadmap-resources"]},
    {"key": "foundations", "file": "foundations.html", "label": "基础知识", "group": "入门学习", "script": "foundations.js",
     "sections": ["foundations"]},
    {"key": "guided", "file": "guided.html", "label": "精读导读", "group": "入门学习", "script": "guided.js",
     "sections": ["guided"]},
    {"key": "advanced", "file": "advanced.html", "label": "进阶专题", "group": "入门学习", "script": "advanced.js",
     "sections": ["advanced"]},
    {"key": "classics", "file": "classics.html", "label": "经典论文", "group": "入门学习", "script": "classics.js",
     "sections": ["classics", "reading"]},
    {"key": "glossary", "file": "glossary.html", "label": "术语表", "group": "入门学习", "script": "glossary.js",
     "sections": ["glossary"]},
    {"key": "anchors", "file": "anchors.html", "label": "锚点论文", "group": "领域调研", "script": "anchors.js",
     "sections": ["anchors"]},
    {"key": "landscape", "file": "landscape.html", "label": "领域全景", "group": "领域调研", "script": "landscape.js",
     "sections": ["map", "paradigms", "trends"]},
    {"key": "areas", "file": "areas.html", "label": "分方向与论文库", "group": "领域调研", "script": "areas.js",
     "sections": ["areas", "papers"]},
    {"key": "ideas", "file": "ideas.html", "label": "研究机会", "group": "研究", "script": "ideas.js",
     "sections": ["ideas"]},
]
# Navigation-only entry: a link to a section of another page (kept where it used to sit in the sidebar).
NAV_ALIASES = [{"key": "method", "href": "index.html#method", "label": "方法与说明", "group": "研究", "alias": True}]
# Element-id prefixes that live on a single page (targets of chips, inline concept ids and diagram links).
PREFIX_PAGE = [["concept-", "foundations.html"], ["module-", "foundations.html"], ["walk-", "guided.html"],
               ["guide-", "guided.html"], ["adv-", "advanced.html"], ["classic-", "classics.html"],
               ["stage-", "roadmap.html"], ["area-", "areas.html"], ["idea-", "ideas.html"], ["anchor-", "anchors.html"]]
BRAND = "3D 临场研究图谱"
SRC, SITE_DIR = ROOT / "src", ROOT / "site"


def page_data(key, ctx):
    """The data slice each page component reads (plus meta/site/xref, which every page gets)."""
    learn, survey = ctx["learn"], ctx["survey"]
    synth = survey.get("synth") or {}
    if key == "home":
        return {"home": {"counts": ctx["counts"], "executive_summary_zh": synth.get("executive_summary_zh", ""),
                         "pageDesc": ctx["page_desc"]}}
    if key == "roadmap":
        return {"roadmap": learn.get("roadmap") or {}}
    if key == "foundations":
        return {"modules": learn.get("modules", []), "rev": ctx["rev"]}
    if key == "guided":
        return {"guided": learn.get("guided", {})}
    if key == "advanced":
        return {"advanced": learn.get("advanced", [])}
    if key == "classics":
        return {"classics": learn.get("classics", []), "themes": learn.get("themes", []),
                "reading_path": synth.get("reading_path", [])}
    if key == "glossary":
        return {"glossary": learn.get("glossary", [])}
    if key == "anchors":
        return {"anchors": survey.get("anchors") or {}}
    if key == "landscape":
        return {"synth": {k: synth.get(k, []) for k in ("field_map", "paradigms", "trends_zh", "grand_challenges_zh", "predictions_zh")}}
    if key == "areas":
        return {"areas": ctx["areas"], "papers": ctx["papers"]}
    if key == "ideas":
        return {"ideas": ctx["ideas"]}
    raise KeyError(key)


def reverse_index(learn):
    """Concept -> guided steps / classics / advanced topics that reference it (shown on concept cards)."""
    walk_by, classic_by, adv_by = {}, {}, {}
    for anchor in ("quark", "ha"):
        for s in (learn.get("guided", {}).get(anchor) or {}).get("walkthrough", []):
            for c in s.get("concept_ids", []):
                walk_by.setdefault(c, []).append({"anchor": anchor, "id": s.get("id"), "title": s.get("title_zh", "")})
    for i, p in enumerate(learn.get("classics", [])):
        for c in p.get("concept_ids", []):
            classic_by.setdefault(c, []).append({"i": i, "title": p.get("title", "")})
    for t in learn.get("advanced", []):
        for c in t.get("prereqs", []):
            adv_by.setdefault(c, []).append(t["id"])
    return {"walkBy": walk_by, "classicBy": classic_by, "advBy": adv_by}


def render_page(page, shell, css, core, data):
    blob = json.dumps(data, ensure_ascii=False)
    # Keep the JSON inert inside <script type="application/json">.
    blob = blob.replace("</", "<\\/").replace("<!--", "<\\u0021--")
    script = core + "\n" + (SRC / "pages" / page["script"]).read_text(encoding="utf-8") + "\n  finishPage();"
    title = BRAND if page["key"] == "home" else f"{page['label']} · {BRAND}"
    out = shell
    for k, v in (("{{TITLE}}", html.escape(title)), ("{{DESCRIPTION}}", html.escape(page.get("description", ""), quote=True)),
                 ("{{STYLE}}", css), ("{{SCRIPT}}", script), ("{{DATA}}", blob)):
        out = out.replace(k, v, 1)
    return out


def write_legacy_redirect(section_page):
    """The old single-page report lived at survey/telepresence-atlas.html; keep that path working as a redirect
    that sends old #anchors to the page that now holds them."""
    cfg = json.dumps({"sectionPage": section_page, "prefixPage": PREFIX_PAGE}, ensure_ascii=False)
    (ROOT / "telepresence-atlas.html").write_text(f"""<!doctype html>
<html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{BRAND}</title>
<script>
(function () {{
  var cfg = {cfg};
  var h = location.hash ? location.hash.slice(1) : "", page = "index.html";
  if (h && /^[A-Za-z0-9._~-]+$/.test(h)) {{
    if (cfg.sectionPage[h]) page = cfg.sectionPage[h];
    else for (var i = 0; i < cfg.prefixPage.length; i++) if (h.indexOf(cfg.prefixPage[i][0]) === 0) {{ page = cfg.prefixPage[i][1]; break; }}
  }} else h = "";
  location.replace("site/" + page + (h ? "#" + h : ""));
}})();
</script>
</head><body><p>{BRAND} 已拆分为多页，请打开 <a href="site/index.html">site/index.html</a>。</p></body></html>
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

    counts = {"concepts": sum(len(m["concepts"]) for m in learn.get("modules", [])), "advanced": len(learn.get("advanced", [])),
              "classics": len(learn.get("classics", [])), "papers": len(papers), "ideas": len(ideas),
              "glossary": len(learn.get("glossary", [])), "areas": len(areas),
              "stages": len((learn.get("roadmap") or {}).get("stages", [])),
              "steps": {k: len(g.get("walkthrough", [])) for k, g in (learn.get("guided") or {}).items()}}
    page_desc = {
        "home": "全站概览、执行摘要、内容导航与调研方法。",
        "roadmap": f"{counts['stages']} 个阶段：每阶段的概念、论文、课程、动手项目和检查题，最后复现两篇锚点论文。",
        "foundations": f"{len(learn.get('modules', []))} 个模块、{counts['concepts']} 个概念：直觉、公式、例子、易错点，以及在两篇锚点论文中的位置。",
        "guided": f"把 Quark（{counts['steps'].get('quark', 0)} 步）和 Ha et al.（{counts['steps'].get('ha', 0)} 步）逐步拆开，每一步链接到所需的基础概念。",
        "advanced": f"{counts['advanced']} 个进阶专题：核心思想、演进时间线和按优先级排序的奠基论文。",
        "classics": f"{counts['classics']} 篇 2026 年前的高影响论文（时间分布图 + 可筛选列表），以及前沿阅读清单。",
        "glossary": f"{counts['glossary']} 条中英术语，可搜索，并链接到基础概念。",
        "anchors": "两篇锚点论文的研究视角精读：精确数字、设计选择、局限与谱系，以及两者的对比与互补。",
        "landscape": "端到端技术栈全景、表示与渲染范式对比、跨方向趋势与重大挑战。",
        "areas": f"{counts['areas']} 个子方向的综述，以及 {counts['papers']} 条可筛选的论文 / 产品 / 标准库。",
        "ideas": f"{counts['ideas']} 个经对抗查新与模拟评审的研究方向。",
        "method": "调研流程、核查方式与使用注意事项（位于概览页底部）。",
    }
    ctx = {"learn": learn, "survey": survey, "areas": areas, "papers": papers, "ideas": ideas,
           "counts": counts, "page_desc": page_desc, "rev": reverse_index(learn)}
    nav = [{k: p[k] for k in ("key", "file", "label", "group")} for p in PAGES]
    nav.extend(NAV_ALIASES)
    section_page = {sid: p["file"] for p in PAGES for sid in p["sections"]}
    xref = {"concepts": {c["id"]: c["name_zh"] for m in learn.get("modules", []) for c in m["concepts"]},
            "adv": {t["id"]: t["title_zh"] for t in learn.get("advanced", [])}}

    shell = (SRC / "shell.html").read_text(encoding="utf-8")
    css = (SRC / "styles.css").read_text(encoding="utf-8")
    core = (SRC / "core.js").read_text(encoding="utf-8")
    SITE_DIR.mkdir(exist_ok=True)
    total = 0
    for page in PAGES:
        page = {**page, "description": page_desc.get(page["key"], "")}
        data = {"meta": meta, "xref": xref,
                "site": {"brand": BRAND, "current": page["key"], "pages": nav, "sectionPage": section_page, "prefixPage": PREFIX_PAGE}}
        data.update(page_data(page["key"], ctx))
        out = SITE_DIR / page["file"]
        out.write_text(render_page(page, shell, css, core, data), encoding="utf-8")
        json.loads(re.search(r'id="data">(.*?)</script>', out.read_text(encoding="utf-8"), re.S).group(1))
        size = out.stat().st_size
        total += size
        print(f"{page['file']:18s} {size / 1024:8.0f} KB")
    write_legacy_redirect(section_page)
    write_artifact_entry((SITE_DIR / "index.html").read_text(encoding="utf-8"))
    print(f"site/: {len(PAGES)} pages, {total / 1024 / 1024:.1f} MB total; stats={stats}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
