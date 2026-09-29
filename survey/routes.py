"""Route table for the redesigned (Tufte) site: navigation, the element-id -> url table used for links and hover
previews, one page composition per article type, and the old-url redirect map. Standard library only.

A page is composed here as a list of blocks that src/tufte/blocks.js renders:
  {"b": "sec", "h": title, "id": ..., "sn"/"mn": note}   starts a section (h2); a missing "h" gives an untitled one
  {"b": "p" | "lines", "t": text, "label": run-in label, "mn"/"sn": note}   paragraphs (blank-line / line split)
  {"b": "h3", "t", "id", "en", "tag", "url", "sn", "mn"}
  {"b": "ul" | "ol", "items": [text | {"label", "t"}]}      {"b": "eqs", "eqs": [...]}      {"b": "qa", "items": [{"q", "a"}]}
  {"b": "res", "items": resources}                            {"b": "refs", "items": [{"left", "k"|"u"|"url", "t", "sub", "gloss", "id"}]}
  {"b": "toc", "groups": [{"h", "k"|"u", "lede", "items": [{"k"|"u", "t", "en", "s", "meta"}]}]}
  {"b": "table", "head": [...], "rows": [[cell]], "wide": bool}  (cell: text or link dict)
  {"b": "timeline", "items": [[year, text]]}   {"b": "kv", "items": [[k, v]]}   {"b": "mtoc", "items": [...]}   {"b": "slot", "name"}
Links are dicts: {"k": element id} (an entry of the xref table, with hover preview), {"u": site url, "t": label} or
{"url": external https url, "t": label}.
"""
import re

BRAND = "3D Telepresence: a field guide"
ANCHOR_SHORT = {"quark": "Quark", "ha": "Ha et al."}
ID_TOKEN = re.compile(r"(a-[a-z0-9]+(?:-[a-z0-9]+)*|[fgdrilnv]-[a-z0-9]+)")
PRIORITY = {"must": "必读", "should": "建议", "optional": "选读"}
DECISION = {"pursue": "建议推进", "pursue_with_repositioning": "重新定位后推进", "drop": "建议放弃"}
VERDICT = {"open": "查新：空白", "partially_scooped": "查新：部分已被做", "scooped": "查新：已被做"}
OVERLAP = {"high": "高", "medium": "中", "low": "低"}
TIER = {"milestone": "里程碑", "important": "重要", "relevant": "相关"}
SHORT_LANE = {"t-ibr-geometry": "经典 IBR 与多视几何", "t-fusion-capture": "深度融合与临场系统", "t-deep-geometry": "深度学习几何",
              "t-neural-rendering": "神经渲染与新视角合成", "t-dynamic-human": "动态场景、4D 与人体", "t-generative-ff": "生成先验、前馈与评测"}
WALK_PARTS = [  # (url suffix, title, source field)
    ("tensor-trace", "张量追踪", "tensor_trace"), ("experiments", "阅读实验", "reading_experiments"),
    ("tradeoffs", "设计权衡", "tradeoffs"), ("faq", "常见问题", "faq"), ("exercises", "练习", "exercises"),
    ("glossary", "论文术语", "glossary"),
]

NAV = [
    {"key": "overview", "label": "Overview", "items": [
        ["Introduction", "index.html"], ["Methodology", "overview/methodology.html"], ["How to use", "overview/how-to-use.html"]]},
    {"key": "basics", "label": "Basics", "items": [
        ["Routes", "basics/routes/index.html"], ["Foundations", "basics/foundations/index.html"],
        ["Advanced topics", "basics/advanced/index.html"], ["Classics", "basics/classics/index.html"], ["Glossary", "basics/glossary.html"]]},
    {"key": "works", "label": "Works", "items": [
        ["Papers", "works/papers/index.html"], ["Walkthrough", "works/walkthrough/index.html"],
        ["Field map", "works/field-map.html"], ["Sub areas", "works/areas/index.html"]]},
    {"key": "future", "label": "Future", "items": [["Directions", "future/index.html"], ["Trends & Challenges", "future/trends.html"]]},
]
# Nav item -> (nav key, element id of that section's first page). Top-level pages chain prev/next in this order.
SECTIONS = [(m["key"], label, url) for m in NAV for label, url in m["items"]]
SECTION_KEY = {"index.html": "top", "overview/methodology.html": "methodology", "overview/how-to-use.html": "howto",
               "basics/routes/index.html": "roadmap", "basics/foundations/index.html": "foundations",
               "basics/advanced/index.html": "advanced", "basics/classics/index.html": "classics",
               "basics/glossary.html": "glossary", "works/papers/index.html": "anchors",
               "works/walkthrough/index.html": "guided", "works/field-map.html": "map",
               "works/areas/index.html": "areas", "future/index.html": "ideas", "future/trends.html": "trends"}
# Where each element id lived in the old 11-page site (for the redirect pages).
OLD_SECTIONS = {
    "index.html": ["top", "summary", "sitemap", "method"], "roadmap.html": ["roadmap", "roadmap-resources"],
    "foundations.html": ["foundations"], "guided.html": ["guided"], "advanced.html": ["advanced"],
    "classics.html": ["classics", "reading"], "glossary.html": ["glossary"], "anchors.html": ["anchors"],
    "landscape.html": ["map", "paradigms", "trends"], "areas.html": ["areas", "papers"], "ideas.html": ["ideas"],
}
OLD_PREFIX = [("concept-", "foundations.html"), ("module-", "foundations.html"), ("walk-", "guided.html"),
              ("guide-", "guided.html"), ("adv-", "advanced.html"), ("classic-", "classics.html"),
              ("stage-", "roadmap.html"), ("area-", "areas.html"), ("idea-", "ideas.html"), ("anchor-", "anchors.html")]


# ---------- text helpers ----------
def first_sentence(text, limit: int) -> str:
    """One-line summary for link previews: the first sentence, cut to about `limit` characters."""
    t = re.sub(r"\s+", " ", str(text or "")).strip()
    m = re.search(r"[。！？]", t)
    if m:
        t = t[:m.end()]
    return t if len(t) <= limit else t[:limit - 1].rstrip("，、；：,;: ") + "…"


def all_strings(x):
    if isinstance(x, str):
        yield x
    elif isinstance(x, dict):
        for v in x.values():
            yield from all_strings(v)
    elif isinstance(x, list):
        for v in x:
            yield from all_strings(v)


def read_minutes(obj) -> int:
    """Reading time at about 500 characters (Chinese characters plus Latin words) per minute."""
    s = " ".join(all_strings(obj))
    return max(1, round((len(re.findall(r"[㐀-鿿]", s)) + len(re.findall(r"[A-Za-z0-9]+", s))) / 500))


def slug(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", str(text).lower()).strip("-")


def fmt_cit(n) -> str:
    try:
        n = int(n)
    except (TypeError, ValueError):
        return "—"
    if n < 0:
        return "—"
    return f"{n / 1000:.0f}k" if n >= 10000 else (f"{n / 1000:.1f}k" if n >= 1000 else str(n))


# ---------- block constructors (None / empty blocks are dropped) ----------
def has(x) -> bool:
    return bool(x.strip()) if isinstance(x, str) else bool(x)


def SEC(h=None, id=None, **kw):
    return {"b": "sec", "h": h, "id": id, **{k: v for k, v in kw.items() if v}}


def P(t, label=None, **kw):
    return {"b": "p", "t": t, **({"label": label} if label else {}), **{k: v for k, v in kw.items() if v}} if has(t) else None


def LINES(t):
    return {"b": "lines", "t": t} if has(t) else None


def H3(t, **kw):
    return {"b": "h3", "t": t, **{k: v for k, v in kw.items() if v}} if has(t) else None


def UL(items, ordered=False):
    items = [x for x in items or [] if has(x if isinstance(x, str) else x.get("t"))]
    return {"b": "ol" if ordered else "ul", "items": items} if items else None


def REFS(items, cls=None):
    items = [x for x in items if x]
    return {"b": "refs", "items": items, **({"cls": cls} if cls else {})} if items else None


def RES(items):
    return {"b": "res", "items": items} if items else None


def QA(items):
    items = [x for x in items if has(x.get("q"))]
    return {"b": "qa", "items": items} if items else None


def TABLE(head, rows, wide=False, cls=None):
    return {"b": "table", "head": head, "rows": rows, "wide": wide, **({"cls": cls} if cls else {})} if rows else None


def TIMELINE(items):
    return {"b": "timeline", "items": items} if items else None


def KV(items):
    items = [x for x in items if has(x[1])]
    return {"b": "kv", "items": items} if items else None


def TOC(groups):
    return {"b": "toc", "groups": groups}


def note(label, t=None, links=None):
    """A side / margin note: a label plus text (rich) or a list of links."""
    if not has(t) and not links:
        return None
    return {"label": label, **({"t": t} if has(t) else {}), **({"links": links} if links else {})}


def clean(blocks):
    """Drop empty blocks and sections left without content."""
    out = []
    for b in blocks:
        if not b:
            continue
        if out and out[-1]["b"] == "sec" and b["b"] == "sec":
            out.pop()
        out.append(b)
    if out and out[-1]["b"] == "sec":
        out.pop()
    return out


# ---------- the element-id table ----------
def xref_table(ctx) -> dict:
    """Element id -> {u: url from the site root, t: title, e: English name, m: where it lives, s: one-line summary,
    n: short label for inline links}. Pages link by element id; hover previews read the same entries."""
    learn, survey, synth = ctx["learn"], ctx["survey"], (ctx["survey"].get("synth") or {})
    x = {}
    for m in learn.get("modules", []):
        where = f"Foundations · {m['id']} {m['title_zh']}"
        x[f"module-{m['id']}"] = {"u": f"basics/foundations/{m['id'].lower()}.html", "t": f"{m['id']} · {m['title_zh']}",
                                  "e": m["title_en"], "m": "Foundations", "s": first_sentence(m.get("goal_zh"), 80)}
        for c in m["concepts"]:
            x[f"concept-{c['id']}"] = {"u": f"basics/foundations/{c['id']}.html", "t": c["name_zh"], "e": c.get("name_en", ""),
                                       "m": where, "s": first_sentence(c.get("tldr_zh"), 120), "n": c["name_zh"].split("：")[0]}
    for t in learn.get("advanced", []):
        x[f"adv-{t['id']}"] = {"u": f"basics/advanced/{t['id']}.html", "t": t["title_zh"], "e": t.get("title_en", ""),
                               "m": "Advanced topics", "s": first_sentence(t.get("overview_zh"), 80)}
    themes = {th["id"]: th for th in learn.get("themes", [])}
    for tid, th in themes.items():
        n = sum(1 for p in learn.get("classics", []) if p.get("theme") == tid)
        x[f"theme-{tid}"] = {"u": f"basics/classics/{tid}.html", "t": th["title_zh"], "e": "", "m": "Classics",
                             "s": f"本主题收录 {n} 篇论文。范围：" + first_sentence(th.get("scope", ""), 90)}
    for i, p in enumerate(learn.get("classics", [])):
        page = f"basics/classics/{p['theme']}.html" if p.get("theme") in themes else "basics/classics/index.html"
        x[f"classic-{i}"] = {"u": f"{page}#classic-{i}", "t": p["title"], "e": "", "m": f"Classics · {p['year']}",
                             "s": first_sentence(p.get("influence_zh"), 80)}
    for i, s in enumerate((learn.get("roadmap") or {}).get("stages", [])):
        x[f"stage-{i}"] = {"u": f"basics/routes/stage-{i + 1}.html", "t": s["title_zh"], "e": "", "m": f"Routes · {s.get('duration_zh', '')}",
                           "s": first_sentence(s.get("goal_zh"), 80), "n": s["title_zh"].split("：")[0]}
    for t in learn.get("glossary", []):
        x[f"term-{slug(t['term_en'])}"] = {"u": f"basics/glossary.html#term-{slug(t['term_en'])}", "t": t.get("term_zh", ""),
                                           "e": t["term_en"] + (f" ({t['abbr']})" if t.get("abbr") else ""),
                                           "m": "Glossary · " + (t.get("category") or ""), "s": first_sentence(t.get("def_zh"), 80)}
    for anchor, g in (learn.get("guided") or {}).items():
        short = ANCHOR_SHORT.get(anchor, anchor)
        x[f"guide-{anchor}"] = {"u": f"works/walkthrough/{anchor}.html", "t": f"{short} 导读", "e": "", "m": "Walkthrough",
                                "s": first_sentence(g.get("story_zh"), 80)}
        for s in g.get("walkthrough", []):
            x[f"walk-{anchor}-{s['id']}"] = {"u": f"works/walkthrough/{anchor}.html#walk-{anchor}-{s['id']}", "t": s.get("title_zh", ""),
                                            "e": "", "m": f"Walkthrough · {short} · {s['id'].upper()}",
                                            "s": first_sentence(s.get("what_zh"), 80), "n": s["id"].upper()}
        for suffix, title, field in WALK_PARTS:
            x[f"wpart-{anchor}-{suffix}"] = {"u": f"works/walkthrough/{anchor}-{suffix}.html", "t": f"{short} · {title}", "e": "",
                                             "m": f"Walkthrough · {short}", "s": part_summary(field, g.get(field) or [])}
    anchors = survey.get("anchors") or {}
    for key in ("quark", "ha"):
        a = anchors.get(key) or {}
        x[f"anchor-{key}"] = {"u": f"works/papers/{key}.html", "t": f"{ANCHOR_SHORT[key]} 精读", "e": (a.get("citation") or {}).get("title", ""),
                              "m": "Papers · 重点论文", "s": first_sentence(a.get("tldr_zh"), 120)}
    x["anchor-cmp"] = {"u": "works/papers/compare.html", "t": "Quark 与 Ha et al.：对比与互补", "e": "", "m": "Papers",
                       "s": first_sentence((anchors.get("compare") or {}).get("philosophy_zh"), 100)}
    x["summary"] = {"u": "works/papers/summary.html", "t": "调研摘要", "e": "Survey summary", "m": "Papers",
                    "s": first_sentence(synth.get("executive_summary_zh"), 100)}
    x["papers"] = {"u": "works/papers/database.html", "t": "论文库", "e": "Paper database", "m": "Papers",
                   "s": f"{len(ctx['papers'])} 条论文、产品和标准，可按方向、重要性和年份筛选。"}
    for a in ctx["areas"]:
        x[f"area-{a['key']}"] = {"u": f"works/areas/{a['key']}.html", "t": a.get("area_title_zh", a["key"]), "e": "", "m": "Sub areas",
                                 "s": first_sentence(a.get("overview_zh"), 80)}
    for rank, it in enumerate(ctx["ideas"], 1):
        sh = it.get("sharpened") or {}
        x[f"idea-{it['id']}"] = {"u": f"future/{it['id']}.html", "t": sh.get("title_zh") or it["name"], "e": sh.get("title_en", ""),
                                 "m": f"Directions · 第 {rank} 名 · 综合 {it['scores'].get('overall')}", "s": first_sentence(sh.get("one_liner"), 90)}
    desc = ctx["page_desc"]
    for label, url in [(lbl, u) for _, lbl, u in SECTIONS]:
        key = SECTION_KEY[url]
        x[key] = {"u": url, "t": ctx["section_title"][key], "e": label, "m": nav_label(url), "s": desc.get(key, "")}
    x["paradigms"] = {"u": "works/field-map.html#paradigms", "t": "表示与渲染范式对比", "e": "Paradigms", "m": "Works · Field map",
                      "s": f"{len(synth.get('paradigms') or [])} 种表示与渲染范式的思路、优劣、代表工作与展望。"}
    x["reading"] = {"u": "basics/classics/index.html#reading", "t": "前沿阅读清单", "e": "Reading list", "m": "Basics · Classics",
                    "s": "按入门 / 进阶 / 前沿三档列出的领域论文（偏 2024–2026），与经典论文互补。"}
    x["roadmap-resources"] = {"u": "basics/routes/index.html#roadmap-resources", "t": "核心课程、教材与工具链", "e": "", "m": "Basics · Routes",
                              "s": "整条学习路线共用的课程、教材和工具。"}
    x["sitemap"] = {"u": "overview/how-to-use.html#sitemap", "t": "站点结构", "e": "Site map", "m": "Overview · How to use",
                    "s": "四个模块、各栏目的内容和推荐阅读顺序。"}
    x["method"] = {"u": "overview/how-to-use.html#method", "t": "关于本站：调研方法与核查说明", "e": "", "m": "Overview · How to use",
                   "s": first_sentence(ctx["meta"].get("method_zh"), 80)}
    return x


def part_summary(field, items) -> str:
    n = len(items)
    return {"tensor_trace": f"逐阶段列出 {n} 个关键张量的形状与含义。", "reading_experiments": f"论文里 {n} 组实验分别怎么读、真正说明了什么。",
            "tradeoffs": f"{n} 个关键设计选择：换来了什么，付出了什么。", "faq": f"初读时最常问的 {n} 个问题。",
            "exercises": f"{n} 道由浅入深的动手练习。", "glossary": f"读这篇论文会遇到的 {n} 个术语。"}.get(field, "")


def nav_label(url) -> str:
    for m in NAV:
        for label, u in m["items"]:
            if u == url:
                return f"{m['label']} · {label}"
    return ""


def ids_in(obj, xref) -> set:
    """Keys of the concepts / advanced topics whose ids appear in the text (rendered as inline links)."""
    out = set()
    for s in all_strings(obj):
        for tok in ID_TOKEN.findall(s):
            for key in (f"concept-{tok}", f"adv-{tok}"):
                if key in xref:
                    out.add(key)
    return out


def refs_of(obj, xref) -> set:
    """Every element id a composed page links to: {"k": id} dicts anywhere, plus ids mentioned in its prose."""
    out = set()

    def walk(v):
        if isinstance(v, dict):
            if isinstance(v.get("k"), str) and v["k"]:
                out.add(v["k"])
            for w in v.values():
                walk(w)
        elif isinstance(v, list):
            for w in v:
                walk(w)
    walk(obj)
    return out | ids_in(obj, xref)


# ---------- shared pieces ----------
def res_items(items):
    return [{"type": r.get("type", ""), "title": r.get("title", ""), "url": r.get("url", ""), "note_zh": r.get("note_zh", "")}
            for r in items or []]


def concept_items(ids, xref, minutes=None):
    out = []
    for cid in ids:
        k = f"concept-{cid}"
        if k in xref:
            out.append({"k": k, "t": xref[k]["t"], "en": xref[k]["e"], "s": xref[k]["s"],
                        **({"meta": f"{minutes[cid]} 分钟"} if minutes and cid in minutes else {})})
    return out


def key_items(keys, xref, meta=None):
    return [{"k": k, "t": xref[k]["t"], "en": xref[k].get("e", ""), "s": xref[k]["s"], **({"meta": meta(k)} if meta else {})}
            for k in keys if k in xref]


def links(keys, xref):
    return [{"k": k} for k in keys if k in xref]


def page(pid, title, body, sub="", meta=None, epigraph="", prereqs=None, lede="", mtoc=False):
    # An epigraph is a line or two; a longer summary reads better as the opening paragraph.
    if len(epigraph or "") > 160:
        epigraph, lede = "", (epigraph + ("\n\n" + lede if lede else ""))
    return {"id": pid, "head": {"title": title, "sub": sub, "meta": meta or [], "epigraph": epigraph,
                                "prereqs": [{"k": k} for k in prereqs or []], "lede": lede},
            "body": clean(body), "toc": mtoc}


def route(path, nav, nav_item, title, pg, crumbs, description="", scripts=None, series=None, head_extra=""):
    return {"path": path, "template": "blocks", "scripts": scripts or [], "nav": nav, "navItem": nav_item, "title": title,
            "page": pg, "crumbs": crumbs, "description": description, "series": series or {}, "head_extra": head_extra}


def chain(routes, up=None):
    """Previous / next links along a list of routes of the same series."""
    for i, r in enumerate(routes):
        s = r["series"]
        if i > 0:
            s["prev"] = routes[i - 1]["page"]["id"]
        if i + 1 < len(routes):
            s["next"] = routes[i + 1]["page"]["id"]
        if up:
            s["up"] = up
    return routes


# ---------- pages ----------
def foundations_routes(ctx, xref):
    learn, minutes = ctx["learn"], ctx["minutes"]
    mods = learn.get("modules", [])
    crumbs0 = [["Basics", ""], ["Foundations", "basics/foundations/index.html"]]
    out = []
    groups = [{"h": x["t"], "k": f"module-{m['id']}", "lede": m.get("goal_zh", ""),
               "items": concept_items([c["id"] for c in m["concepts"]], xref, minutes)}
              for m in mods for x in [xref[f"module-{m['id']}"]]]
    index = route("basics/foundations/index.html", "basics", "basics/foundations/index.html", "基础知识",
                  page("foundations", "基础知识", [TOC(groups)], sub="Foundations",
                       meta=[f"{len(mods)} 个模块 · {sum(len(m['concepts']) for m in mods)} 个概念"], lede=ctx["overview"]["ledes"].get("foundations") or ctx["meta"].get("foundations_lede", "")),
                  [["Basics", ""], ["Foundations", ""]], ctx["page_desc"]["foundations"])
    mod_routes = []
    for m in mods:
        key = f"module-{m['id']}"
        total = sum(minutes.get(c["id"], 1) for c in m["concepts"])
        body = [SEC(None, "intro"), P(m.get("intro_zh")), SEC("怎么学", "study"), LINES(m.get("study_tips_zh")),
                SEC(f"本模块的 {len(m['concepts'])} 个概念", "concepts"),
                TOC([{"items": concept_items([c["id"] for c in m["concepts"]], xref, minutes)}])]
        mod_routes.append(route(xref[key]["u"], "basics", "basics/foundations/index.html", xref[key]["t"],
                                page(key, xref[key]["t"], body, sub=m["title_en"], epigraph=m.get("goal_zh", ""),
                                     meta=[f"{len(m['concepts'])} 个概念 · 读完约 {total} 分钟"]),
                                crumbs0 + [[f"{m['id']} {m['title_zh']}", ""]], xref[key]["s"]))
    chain(mod_routes, {"u": "basics/foundations/index.html", "t": "Foundations 目录"})
    return [index] + mod_routes


def advanced_routes(ctx, xref):
    learn = ctx["learn"]
    topics = learn.get("advanced", [])
    classics_by_adv = {}
    for i, p in enumerate(learn.get("classics", [])):
        for a in p.get("adv_ids", []):
            classics_by_adv.setdefault(a, []).append(i)
    index = route("basics/advanced/index.html", "basics", "basics/advanced/index.html", "进阶专题",
                  page("advanced", "进阶专题", [TOC([{"items": key_items([f"adv-{t['id']}" for t in topics], xref,
                                                                          lambda k: f"{len(next(t for t in topics if 'adv-' + t['id'] == k).get('papers', []))} 篇奠基论文")}])],
                       sub="Advanced topics", meta=[f"{len(topics)} 个专题"], lede=ctx["meta"].get("advanced_lede", "")),
                  [["Basics", ""], ["Advanced topics", ""]], ctx["page_desc"]["advanced"])
    out = []
    for t in topics:
        key = f"adv-{t['id']}"
        papers = t.get("papers", [])
        body = [SEC(None, "overview"), P(t.get("overview_zh")),
                SEC("核心思想", "key-ideas")] + [b for k in t.get("key_ideas", []) for b in (H3(k.get("name_zh")), P(k.get("explain_zh")))] + [
            SEC("关键公式", "equations"), {"b": "eqs", "eqs": t["equations"]} if t.get("equations") else None,
            SEC("演进", "evolution"), TIMELINE([[e.get("year"), e.get("milestone_zh", "")] for e in sorted(t.get("evolution", []), key=lambda e: e.get("year") or 0)]),
            SEC("奠基论文", "papers"),
            REFS([{"left": PRIORITY.get(p.get("priority"), "选读"), "url": p.get("url", ""), "t": p.get("title", ""),
                   "sub": " · ".join(str(v) for v in [p.get("authors"), p.get("venue"), p.get("year")] if v) + f" · 引用 {fmt_cit(p.get('citations'))}",
                   "gloss": p.get("role_zh", "")} for p in papers]),
            SEC("争论与分歧", "debates"), UL(t.get("debates_zh")),
            SEC("开放问题", "open-questions"), UL(t.get("open_questions_zh")),
            SEC("与重点论文的关系", "relation"), P(t.get("relation_to_anchors_zh")),
            SEC("延伸阅读", "further"), H3("学习资源") if t.get("resources") else None, RES(res_items(t.get("resources"))),
            H3("相关经典论文") if classics_by_adv.get(t["id"]) else None,
            REFS([{"left": str(learn["classics"][i]["year"]), "k": f"classic-{i}"} for i in classics_by_adv.get(t["id"], [])], "papers"),
        ]
        out.append(route(xref[key]["u"], "basics", "basics/advanced/index.html", t["title_zh"],
                         page(key, t["title_zh"], body, sub=t.get("title_en", ""), prereqs=[f"concept-{c}" for c in t.get("prereqs", [])],
                              meta=[f"{len(papers)} 篇奠基论文"]),
                         [["Basics", ""], ["Advanced topics", "basics/advanced/index.html"]], xref[key]["s"]))
    chain(out, {"u": "basics/advanced/index.html", "t": "Advanced topics 目录"})
    return [index] + out


def classic_entry(i, p, xref, themes):
    concept_links = links([f"concept-{c}" for c in p.get("concept_ids", [])] + [f"adv-{a}" for a in p.get("adv_ids", [])], xref)
    info = [str(p.get("year") or ""), p.get("authors", ""), p.get("venue", ""),
            (f"{p.get('citations_source') or ''} 引用 {p['citations']}".strip() if isinstance(p.get("citations"), int) and p["citations"] >= 0 else ""),
            f"难度：{p['difficulty']}" if p.get("difficulty") else "", "必读" if p.get("must_read") else ""]
    return [H3(p["title"], id=f"classic-{i}", url=p.get("url", ""), sn=note("与重点论文的联系", p.get("anchor_link_zh"))),
            {"b": "note", "t": " · ".join(v for v in info if v)},
            P(p.get("influence_zh"), label="为什么有影响力", mn=note("相关概念与专题", links=concept_links) if concept_links else None),
            P(p.get("contributions_zh"), label="主要贡献")]


def chart_data(classics, themes, xref):
    return {"lanes": [{"id": t["id"], "label": SHORT_LANE.get(t["id"], t["title_zh"])} for t in themes],
            "points": [{"y": p["year"], "c": p.get("citations"), "m": bool(p.get("must_read")), "t": p["title"], "v": p.get("venue", ""),
                        "u": xref[f"classic-{i}"]["u"], "lane": p.get("theme")} for i, p in enumerate(classics)
                       if p.get("theme") in {t["id"] for t in themes}]}


def classics_routes(ctx, xref):
    learn, synth = ctx["learn"], ctx["survey"].get("synth") or {}
    classics, themes = learn.get("classics", []), learn.get("themes", [])
    theme_ids = [t["id"] for t in themes]
    must = [{"h": xref[f"theme-{t}"]["t"], "k": f"theme-{t}",
             "items": [{"k": f"classic-{i}", "t": p["title"], "meta": str(p["year"])} for i, p in enumerate(classics) if p.get("must_read") and p.get("theme") == t]}
            for t in theme_ids]
    body = [SEC("时间线", "timeline"), {"b": "slot", "name": "classics-chart"},
            SEC("六个主题", "themes"), TOC([{"items": key_items([f"theme-{t}" for t in theme_ids], xref)}]),
            SEC("必读清单", "must-read"), TOC([g for g in must if g["items"]]),
            SEC("前沿阅读清单", "reading"),
            P("按入门 / 进阶 / 前沿三档列出的领域论文（偏 2024–2026），与上面的经典论文互补。")]
    for s in synth.get("reading_path", []):
        body += [H3(s.get("stage_zh")), REFS([{"left": str(n), "url": it.get("url", ""), "t": it.get("title", ""), "gloss": it.get("why_zh", "")}
                                              for n, it in enumerate(s.get("items", []), 1)])]
    index = route("basics/classics/index.html", "basics", "basics/classics/index.html", "经典论文",
                  page("classics", "经典论文", body, sub="Classics", meta=[f"{len(classics)} 篇 · {len(themes)} 个主题"],
                       lede=ctx["overview"]["ledes"].get("classics") or ctx["meta"].get("classics_lede", "")),
                  [["Basics", ""], ["Classics", ""]], ctx["page_desc"]["classics"], scripts=["classics-chart.js"])
    index["extra"] = {"chart": chart_data(classics, themes, xref)}
    out = []
    for t in themes:
        key = f"theme-{t['id']}"
        mine = [(i, p) for i, p in enumerate(classics) if p.get("theme") == t["id"]]
        also = [(i, p) for i, p in enumerate(classics) if p.get("theme") != t["id"] and t["id"] in (p.get("themes") or [])]
        body = [SEC(None, "list"), P(f"本主题收录 {len(mine)} 篇论文，按年份排列。范围：{t.get('scope', '')}"),
                {"b": "slot", "name": "classics-chart"},
                REFS([{"left": str(p["year"]), "u": f"#classic-{i}", "t": p["title"], "tag": "必读" if p.get("must_read") else ""} for i, p in mine], "papers"),
                SEC("论文", "papers")] + [b for i, p in mine for b in classic_entry(i, p, xref, themes)]
        if also:
            body += [SEC("也属于本主题的论文", "also"), REFS([{"left": str(p["year"]), "k": f"classic-{i}"} for i, p in also], "papers")]
        out.append(route(xref[key]["u"], "basics", "basics/classics/index.html", t["title_zh"],
                         page(key, t["title_zh"], body, sub="Classics", meta=[f"{len(mine)} 篇论文"]),
                         [["Basics", ""], ["Classics", "basics/classics/index.html"]], xref[key]["s"], scripts=["classics-chart.js"]))
        out[-1]["extra"] = {"chart": chart_data(classics, [t], xref)}
    chain(out, {"u": "basics/classics/index.html", "t": "Classics 目录"})
    return [index] + out


def routes_routes(ctx, xref):
    rm = ctx["learn"].get("roadmap") or {}
    stages = rm.get("stages", [])
    body = [SEC(None, "overview"), P(rm.get("overview_zh")),
            SEC(f"{len(stages)} 个阶段", "stages"),
            TOC([{"items": key_items([f"stage-{i}" for i in range(len(stages))], xref, lambda k: stages[int(k[6:])].get("duration_zh", ""))}]),
            SEC("核心课程与教材", "roadmap-resources"), RES(res_items(rm.get("courses_books"))),
            SEC("工具链", "tools"), REFS([{"url": t.get("url", ""), "t": t.get("name", ""), "gloss": t.get("use_zh", "")} for t in rm.get("tools", [])]),
            SEC("学习建议", "tips"), UL(rm.get("tips_zh"))]
    index = route("basics/routes/index.html", "basics", "basics/routes/index.html", "学习路线",
                  page("roadmap", "学习路线", body, sub="Routes", meta=[f"{len(stages)} 个阶段"]),
                  [["Basics", ""], ["Routes", ""]], ctx["page_desc"]["roadmap"])
    out = []
    for i, s in enumerate(stages):
        key = f"stage-{i}"
        pr = s.get("project") or {}
        body = [SEC("这一阶段的概念", "concepts"), TOC([{"items": concept_items(s.get("concept_ids", []), xref, ctx["minutes"])}]),
                SEC("进阶专题", "advanced"), TOC([{"items": key_items([f"adv-{a}" for a in s.get("advanced_ids", [])], xref)}]) if s.get("advanced_ids") else None,
                SEC("要读的论文", "papers"), REFS([{"left": str(n), "url": p.get("url", ""), "t": p.get("title", ""), "gloss": p.get("why_zh", "")}
                                                   for n, p in enumerate(s.get("papers", []), 1)]),
                SEC("课程与资料", "resources"), RES(res_items(s.get("resources"))),
                SEC("动手项目：" + pr.get("title_zh", ""), "project"), P(pr.get("task_zh")),
                P(pr.get("deliverable_zh"), label="交付物"), P(pr.get("hints_zh"), label="提示"),
                SEC("学完应能回答", "checkpoint"), UL(s.get("checkpoint_zh"))]
        out.append(route(xref[key]["u"], "basics", "basics/routes/index.html", s["title_zh"],
                         page(key, s["title_zh"], body, epigraph=s.get("goal_zh", ""), meta=[s.get("duration_zh", "")]),
                         [["Basics", ""], ["Routes", "basics/routes/index.html"]], xref[key]["s"]))
    chain(out, {"u": "basics/routes/index.html", "t": "Routes 目录"})
    return [index] + out


def glossary_route(ctx, xref):
    terms = ctx["learn"].get("glossary", [])
    body = [{"b": "slot", "name": "glossary"}]
    r = route("basics/glossary.html", "basics", "basics/glossary.html", "术语表",
              page("glossary", "术语表", body, sub="Glossary", meta=[f"{len(terms)} 条"],
                   lede="读论文时遇到的缩写和术语，可按中英文或缩写搜索。点右侧的概念可跳到对应的基础概念页。"),
              [["Basics", ""], ["Glossary", ""]], ctx["page_desc"]["glossary"], scripts=["glossary.js"])
    r["extra"] = {"glossary": [{"id": f"term-{slug(t['term_en'])}", "en": t["term_en"], "abbr": t.get("abbr", ""), "zh": t.get("term_zh", ""),
                                "def": t.get("def_zh", ""), "cat": t.get("category", ""),
                                "k": f"concept-{t['concept_id']}" if t.get("concept_id") else ""} for t in terms]}
    return [r]


def paper_page(key, a, xref):
    c = a.get("citation") or {}
    lin = a.get("lineage") or {}
    meta = [" · ".join(v for v in [c.get("authors"), c.get("affiliations")] if v), f"{c.get('venue', '')}"]
    body = [SEC(None, "links"), REFS([{"left": "论文", "url": c.get("url", ""), "t": c.get("title", "")},
                                      {"left": "主页", "url": c.get("project_page", ""), "t": c.get("project_page", "")} if c.get("project_page") else None,
                                      {"left": "代码", "t": c.get("code_status", "")} if c.get("code_status") else None]),
            SEC("问题设定", "problem"), P(a.get("problem_setting_zh")),
            SEC("流水线", "pipeline"), UL([{"label": s.get("stage", ""), "t": s.get("detail", "")} for s in a.get("pipeline_zh", [])], ordered=False),
            SEC("系统与性能", "performance"), KV([[x.get("item", ""), x.get("value", "")] for x in a.get("system_perf", [])]),
            SEC("关键设计选择", "design")] + [b for d in a.get("key_design_choices_zh", []) for b in (
                H3(d.get("choice")), P(d.get("rationale"), label="理由"), P(d.get("alternatives_rejected"), label="被放弃的替代方案"))] + [
            SEC("训练", "training"), P(a.get("training_zh")),
            SEC("实验结果", "results"), UL([{"label": r.get("dataset", ""), "t": r.get("finding", "")} for r in a.get("results_zh", [])]),
            SEC("消融", "ablations"), UL(a.get("ablations_zh")),
            SEC("局限", "limitations"), H3("作者承认的局限"), UL(a.get("limitations_stated_zh")),
            H3("精读发现的未言明问题"), UL(a.get("limitations_unstated_zh")),
            SEC("谱系", "lineage"), H3("前序工作"),
            REFS([{"left": str(p.get("year", "")), "url": p.get("url", ""), "t": p.get("title", ""), "gloss": p.get("note_zh", "")} for p in lin.get("predecessors", [])]),
            H3("后续 / 竞争工作"),
            REFS([{"left": str(p.get("year", "")), "url": p.get("url", ""), "t": p.get("title", ""), "gloss": p.get("note_zh", "")} for p in lin.get("successors", [])]),
            SEC("对 3D 临场的启示", "takeaways"), UL(a.get("takeaways_for_telepresence_zh")),
            SEC("延伸阅读", "further"), TOC([{"items": key_items([f"guide-{key}"] + [f"wpart-{key}-{s}" for s, _, _ in WALK_PARTS], xref)}])]
    return body, meta


def papers_routes(ctx, xref):
    survey = ctx["survey"]
    anchors, synth = survey.get("anchors") or {}, survey.get("synth") or {}
    crumbs = [["Works", ""], ["Papers", "works/papers/index.html"]]
    index = route("works/papers/index.html", "works", "works/papers/index.html", "重点论文与论文库",
                  page("anchors", "重点论文与论文库", [TOC([{"items": key_items(["anchor-quark", "anchor-ha", "anchor-cmp", "summary", "papers"], xref)}])],
                       sub="Papers", lede="两篇重点论文的研究视角精读：精确数字、设计选择、局限与谱系，以及两者的对比。想从零读懂，先看 Walkthrough 里的导读长文。"),
                  [["Works", ""], ["Papers", ""]], ctx["page_desc"]["anchors"])
    out = []
    for key in ("quark", "ha"):
        a = anchors.get(key) or {}
        body, meta = paper_page(key, a, xref)
        out.append(route(f"works/papers/{key}.html", "works", "works/papers/index.html", xref[f"anchor-{key}"]["t"],
                         page(f"anchor-{key}", xref[f"anchor-{key}"]["t"], body, sub=(a.get("citation") or {}).get("title", ""),
                              meta=meta, epigraph=a.get("tldr_zh", "")), crumbs, xref[f"anchor-{key}"]["s"]))
    cmp_ = anchors.get("compare") or {}
    body = [SEC("逐项对比", "table"), TABLE(["维度", "Quark", "Ha et al."], [[r.get("dimension", ""), r.get("quark", ""), r.get("ha", "")] for r in cmp_.get("comparison_table", [])], wide=True),
            SEC("两种设计哲学", "philosophy"), P(cmp_.get("philosophy_zh")),
            SEC("互补性", "complementarity"), P(cmp_.get("complementarity_zh")),
            SEC("取两者之长的临场系统草图", "sketch"), P(cmp_.get("combined_system_sketch_zh")),
            SEC("共同盲区", "blindspots"), UL(cmp_.get("shared_blindspots_zh"))]
    out.append(route("works/papers/compare.html", "works", "works/papers/index.html", xref["anchor-cmp"]["t"],
                     page("anchor-cmp", xref["anchor-cmp"]["t"], body, sub="Quark vs. Ha et al."), crumbs, xref["anchor-cmp"]["s"]))
    out.append(route("works/papers/summary.html", "works", "works/papers/index.html", "调研摘要",
                     page("summary", "调研摘要", [SEC(None, "text"), P(synth.get("executive_summary_zh"))], sub="Survey summary",
                          lede=ctx["meta"].get("subtitle", "")),
                     crumbs, xref["summary"]["s"]))
    db = route("works/papers/database.html", "works", "works/papers/index.html", "论文库",
               page("papers", "论文库", [{"b": "slot", "name": "database"}], sub="Paper database", meta=[f"{len(ctx['papers'])} 条"],
                    lede="按方向、重要性、年份筛选，按年份倒序。同一篇工作出现在多个方向时会合并并标注全部方向。"),
               crumbs, xref["papers"]["s"], scripts=["database.js"])
    db["extra"] = {"papers": ctx["papers"], "areaNames": {a["key"]: a.get("area_title_zh", a["key"]) for a in ctx["areas"]}}
    out.append(db)
    chain(out, {"u": "works/papers/index.html", "t": "Papers 目录"})
    return [index] + out


def walk_step(anchor, s, xref):
    need = links([f"concept-{c}" for c in s.get("concept_ids", [])] + [f"adv-{a}" for a in s.get("adv_ids", [])], xref)
    return [SEC(f"{s['id'].upper()} · {s.get('title_zh', '')}", f"walk-{anchor}-{s['id']}", sn=note("论文位置", s.get("paper_ref"))),
            P(s.get("what_zh"), label="这一步做什么", mn=note("需要的基础", links=need) if need else None),
            P(s.get("plain_zh"), mn=note("类比", s.get("analogy_zh"))),
            {"b": "eqs", "eqs": s["equations"]} if s.get("equations") else None,
            P(s.get("numbers_zh"), label="具体数字"), P(s.get("why_design_zh"), label="为什么这样设计"),
            P(s.get("pitfalls_zh"), label="容易误解的地方"),
            QA([{"q": s.get("check_q_zh", ""), "a": s.get("check_a_zh", "")}])]


def walk_part_body(field, items, xref):
    if field == "tensor_trace":
        return [SEC(None, "table"), TABLE(["阶段", "张量", "形状", "说明"], [[r.get("stage_zh", ""), r.get("tensor", ""), r.get("shape", ""), r.get("note_zh", "")] for r in items], wide=True)]
    if field == "reading_experiments":
        return [b for r in items for b in (H3(r.get("item")), P(r.get("how_to_read_zh")), P(r.get("takeaway_zh"), label="真正说明了什么"))]
    if field == "tradeoffs":
        return [b for r in items for b in (H3(r.get("choice_zh")), P(r.get("gain_zh"), label="换来的"), P(r.get("cost_zh"), label="付出的"))]
    if field == "faq":
        return [b for r in items for b in (H3(r.get("q_zh")), P(r.get("a_zh")))]
    if field == "exercises":
        out = []
        for x in items:
            need = links([f"concept-{c}" for c in x.get("concept_ids", [])], xref)
            out += [H3(x.get("title_zh"), tag=x.get("level", "")), P(x.get("task_zh"), mn=note("概念", links=need) if need else None),
                    P(x.get("expected_zh"), label="预期结果"), P(x.get("hint_zh"), label="提示")]
        return out
    if field == "glossary":
        return [SEC(None, "terms"), REFS([{"t": t.get("term_zh", ""), "sub": t.get("term_en", ""), "gloss": t.get("def_zh", "")} for t in items], "terms")]
    return []


def walkthrough_routes(ctx, xref):
    guided = ctx["learn"].get("guided") or {}
    groups = [{"h": xref[f"guide-{a}"]["t"], "k": f"guide-{a}",
               "items": key_items([f"guide-{a}"] + [f"wpart-{a}-{s}" for s, _, _ in WALK_PARTS], xref)} for a in ("quark", "ha") if a in guided]
    index = route("works/walkthrough/index.html", "works", "works/walkthrough/index.html", "精读导读",
                  page("guided", "精读导读", [TOC(groups)], sub="Walkthrough", lede=ctx["overview"]["ledes"].get("guided") or ctx["meta"].get("guided_lede", "")),
                  [["Works", ""], ["Walkthrough", ""]], ctx["page_desc"]["guided"])
    out = [index]
    anchors = ctx["survey"].get("anchors") or {}
    for a in ("quark", "ha"):
        g = guided.get(a)
        if not g:
            continue
        short, steps = ANCHOR_SHORT[a], g.get("walkthrough", [])
        before = REFS([{"k": f"concept-{b['concept_id']}", "gloss": b.get("why_zh", "")} for b in g.get("before_you_read", [])
                       if f"concept-{b['concept_id']}" in xref])
        body = [SEC(None, "story"), {"b": "mtoc", "items": [{"u": f"#walk-{a}-{s['id']}", "t": f"{s['id'].upper()} {s.get('title_zh', '')}"} for s in steps]},
                P(g.get("story_zh")),
                SEC("流水线", "pipeline"), P("点击方框跳到对应步骤。"), {"b": "slot", "name": "diagram", "which": a},
                SEC("读之前先掌握", "before"), before]
        body += [b for s in steps for b in walk_step(a, s, xref)]
        body += [SEC("配套文章", "parts"), TOC([{"items": key_items([f"wpart-{a}-{s}" for s, _, _ in WALK_PARTS], xref)}])]
        cit = (anchors.get(a) or {}).get("citation") or {}
        crumbs = [["Works", ""], ["Walkthrough", "works/walkthrough/index.html"]]
        long_r = route(f"works/walkthrough/{a}.html", "works", "works/walkthrough/index.html", xref[f"guide-{a}"]["t"],
                       page(f"guide-{a}", xref[f"guide-{a}"]["t"], body, sub=cit.get("title", ""),
                            meta=[f"{len(steps)} 步", {"k": f"anchor-{a}", "t": f"{short} 精读"}], mtoc=True),
                       crumbs, xref[f"guide-{a}"]["s"], scripts=["diagram.js"])
        parts = []
        for suffix, title, field in WALK_PARTS:
            key = f"wpart-{a}-{suffix}"
            parts.append(route(xref[key]["u"], "works", "works/walkthrough/index.html", xref[key]["t"],
                               page(key, xref[key]["t"], walk_part_body(field, g.get(field) or [], xref), sub=cit.get("title", ""),
                                    meta=["配套文章：", {"k": f"guide-{a}", "t": f"回到 {short} 导读"}], lede=xref[key]["s"]),
                               crumbs + [[f"{short} 导读", f"works/walkthrough/{a}.html"]], xref[key]["s"]))
        chain(parts, {"u": f"works/walkthrough/{a}.html", "t": f"{short} 导读"})
        out += [long_r] + parts
    return out


def fieldmap_route(ctx, xref):
    synth = ctx["survey"].get("synth") or {}
    body = [SEC("端到端技术栈", "map"), P("从采集到显示与交互，每一层的最新水平、成熟度（1 = 研究原型，5 = 已产品化）与当前瓶颈。")]
    for L in synth.get("field_map", []):
        try:
            m = max(0, min(5, round(float(L.get("maturity") or 0))))
        except ValueError:
            m = 0
        body += [H3(L.get("layer_zh"), en=L.get("layer_en", ""), tag=f"{'●' * m}{'○' * (5 - m)} 成熟度 {m} / 5"),
                 P("、".join(L.get("components_zh", [])), label="组成"), P(L.get("state_of_art_zh")), P(L.get("bottleneck_zh"), label="瓶颈")]
    body += [SEC("表示与渲染范式对比", "paradigms")]
    for p in synth.get("paradigms", []):
        body += [H3(p.get("name")), P(p.get("idea_zh"), label="核心思路"), P(p.get("strengths_zh"), label="优势"),
                 P(p.get("weaknesses_zh"), label="劣势"), P("；".join(p.get("exemplars", [])), label="代表工作"), P(p.get("outlook_zh"), label="展望")]
    return [route("works/field-map.html", "works", "works/field-map.html", "领域全景",
                  page("map", "领域全景", body, sub="Field map", meta=[f"{len(synth.get('field_map', []))} 层技术栈 · {len(synth.get('paradigms', []))} 种范式"]),
                  [["Works", ""], ["Field map", ""]], ctx["page_desc"]["map"])]


def areas_routes(ctx, xref):
    areas, papers = ctx["areas"], ctx["papers"]
    count = {a["key"]: sum(1 for p in papers if a["key"] in p.get("areas", [])) for a in areas}
    index = route("works/areas/index.html", "works", "works/areas/index.html", "子方向",
                  page("areas", "子方向", [TOC([{"items": key_items([f"area-{a['key']}" for a in areas], xref,
                                                                    lambda k: f"{count[k[5:]]} 篇")}])],
                       sub="Sub areas", meta=[f"{len(areas)} 个子方向"],
                       lede="每个方向包含演进脉络、子主题、时间线、趋势与开放问题；论文条目统一收在论文库，可按方向筛选。"),
                  [["Works", ""], ["Sub areas", ""]], ctx["page_desc"]["areas"])
    out = []
    for a in areas:
        key = f"area-{a['key']}"
        body = [SEC(None, "overview"), P(a.get("overview_zh")), SEC("子主题", "subtopics")]
        for s in a.get("subtopics", []):
            body += [H3(s.get("name_zh"), en=s.get("name_en", "")), P(s.get("summary_zh")),
                     P("；".join(s.get("representative_works", [])), label="代表")]
        body += [SEC("时间线", "timeline"), TIMELINE([[t.get("year"), t.get("event_zh", "")] for t in sorted(a.get("timeline", []), key=lambda t: t.get("year") or 0)]),
                 SEC("趋势", "trends"), UL(a.get("trends_zh")), SEC("开放问题", "open-problems"), UL(a.get("open_problems_zh")),
                 SEC("与重点论文的关系", "relation"), P(a.get("relation_to_anchors_zh")),
                 SEC("本方向论文", "works"), REFS([{"u": f"works/papers/database.html?area={a['key']}", "t": f"在论文库中查看本方向的 {count[a['key']]} 条论文"}])]
        out.append(route(xref[key]["u"], "works", "works/areas/index.html", a.get("area_title_zh", a["key"]),
                         page(key, a.get("area_title_zh", a["key"]), body, meta=[f"{count[a['key']]} 篇论文 · {len(a.get('subtopics', []))} 个子主题"]),
                         [["Works", ""], ["Sub areas", "works/areas/index.html"]], xref[key]["s"]))
    chain(out, {"u": "works/areas/index.html", "t": "Sub areas 目录"})
    return [index] + out


def ideas_routes(ctx, xref):
    ideas = ctx["ideas"]
    rows = []
    for rank, it in enumerate(ideas, 1):
        s = it.get("scores") or {}
        rows.append([str(rank), {"k": f"idea-{it['id']}"}, DECISION.get(it["decision"], it["decision"]),
                     VERDICT.get(it["novelty"]["verdict"], it["novelty"]["verdict"]).replace("查新：", ""),
                     str(s.get("overall", "")), str(s.get("novelty", "")), str(s.get("significance", "")),
                     str(s.get("feasibility", "")), str(s.get("telepresence_fit", ""))])
    index = route("future/index.html", "future", "future/index.html", "研究方向",
                  page("ideas", "研究方向", [SEC("排行", "ranking"), TABLE(["#", "方向", "建议", "查新", "综合", "新颖", "意义", "可行", "临场契合"], rows, wide=True, cls="rank")],
                       sub="Directions", meta=[f"{len(ideas)} 个方向"], lede=ctx["overview"]["ledes"].get("ideas") or ctx["meta"].get("ideas_lede", "")),
                  [["Future", ""], ["Directions", ""]], ctx["page_desc"]["ideas"])
    out = []
    for rank, it in enumerate(ideas, 1):
        key = f"idea-{it['id']}"
        sh, ex, nov, ef, s = it.get("sharpened") or {}, it.get("experiments") or {}, it.get("novelty") or {}, it.get("effort") or {}, it.get("scores") or {}
        body = [SEC("评分", "scores"), KV([["综合", str(s.get("overall", ""))], ["新颖", str(s.get("novelty", ""))], ["意义", str(s.get("significance", ""))],
                                          ["可行", str(s.get("feasibility", ""))], ["临场契合", str(s.get("telepresence_fit", ""))]]),
                SEC("核心论点（可证伪）", "claim"), P(sh.get("core_claim")),
                SEC("关键洞察", "insight"), P(sh.get("key_insight")),
                SEC("方法", "method"), P(sh.get("method")),
                SEC("为什么不是工程改进", "not-engineering"), P(sh.get("why_not_engineering")),
                SEC("与已有工作的区分", "differentiation"), P(sh.get("differentiation")),
                SEC("查新后剩余的可辩护新意", "novel-angle"), P(nov.get("remaining_novel_angle")),
                SEC("主要撞车风险（查新找到的相近工作）", "threats"),
                REFS([{"left": OVERLAP.get(t.get("overlap"), t.get("overlap", "")), "url": t.get("url", ""), "t": t.get("title", ""),
                       "sub": " · ".join(str(v) for v in [t.get("year"), t.get("venue"), "重叠度 " + OVERLAP.get(t.get("overlap"), str(t.get("overlap", "")))] if v),
                       "gloss": "重叠：" + (t.get("what_overlaps") or "") + "\n差异：" + (t.get("what_remains_different") or "")} for t in nov.get("threats", [])]),
                SEC("实验设计", "experiments"), H3("数据集"), UL(ex.get("datasets")), H3("对比基线"), UL(ex.get("baselines")),
                H3("指标"), UL(ex.get("metrics")), H3("关键消融"), UL(ex.get("key_ablations")),
                H3("需要自建采集" if ex.get("needs_custom_capture") else "采集说明") if ex.get("capture_notes") else None, P(ex.get("capture_notes")),
                SEC("两周内的验证实验", "two-weeks"), P(it.get("first_two_week_test")),
                SEC("止损标准", "kill"), P(it.get("kill_criteria")),
                SEC("审稿人可能的质疑与回应", "objections")] + [b for o in it.get("reviewer_objections", []) for b in (
                    P(o.get("objection"), label="质疑"), P(o.get("rebuttal"), label="回应"))] + [
                SEC("投入", "effort"), KV([["周期", ef.get("months", "")], ["人力", ef.get("people", "")], ["算力", ef.get("compute", "")], ["目标会议", it.get("venue", "")]]),
                SEC("可组合的方向", "synergies"), P(it.get("synergies"))]
        out.append(route(xref[key]["u"], "future", "future/index.html", xref[key]["t"],
                         page(key, xref[key]["t"], body, sub=sh.get("title_en", ""), epigraph=sh.get("one_liner", ""),
                              meta=[f"第 {rank} 名", DECISION.get(it["decision"], it["decision"]), VERDICT.get(nov.get("verdict"), nov.get("verdict", ""))]),
                         [["Future", ""], ["Directions", "future/index.html"]], xref[key]["s"]))
    chain(out, {"u": "future/index.html", "t": "Directions 目录"})
    return [index] + out


def trends_route(ctx, xref):
    synth = ctx["survey"].get("synth") or {}
    body = [SEC("跨方向趋势", "trends-list")]
    for n, t in enumerate(synth.get("trends_zh", []), 1):
        body += [H3(f"{n}. {t.get('trend', '')}"), P(t.get("evidence"), label="证据"), P(t.get("implication"), label="含义")]
    body += [SEC("重大挑战", "challenges")]
    for n, g in enumerate(synth.get("grand_challenges_zh", []), 1):
        body += [H3(f"{n}. {g.get('title', '')}"), P(g.get("description")), P(g.get("why_hard"), label="为什么难"),
                 P(g.get("promising_directions"), label="有希望的方向")]
    body += [SEC("未来 1–3 年判断", "predictions"), UL(synth.get("predictions_zh"), ordered=True)]
    return [route("future/trends.html", "future", "future/trends.html", "趋势与挑战",
                  page("trends", "趋势与挑战", body, sub="Trends & Challenges"),
                  [["Future", ""], ["Trends & Challenges", ""]], ctx["page_desc"]["trends"])]


def overview_routes(ctx, xref, legacy_home):
    """Introduction, Methodology and How to use: text written for the redesign (data/site/overview.json)."""
    meta, desc, ov = ctx["meta"], ctx["page_desc"], ctx["overview"]
    intro, method, howto = ov["intro"], ov["methodology"], ov["howto"]

    body = []
    for sec in intro["sections"]:
        body += [SEC(sec["h"], sec["id"]), P(sec.get("t")),
                 UL([{"label": a, "t": b} for a, b in sec.get("items", [])], ordered=True), P(sec.get("after"))]
        if sec.get("paths"):
            body.append(REFS([{"left": who, "k": k, "gloss": why} for who, k, why in sec["paths"]]))
        if sec.get("links"):
            body.append(TOC([{"items": key_items(sec["links"], xref)}]))
    home = route("index.html", "overview", "index.html", BRAND,
                 page("top", BRAND, body, epigraph=intro["epigraph"]),
                 [["Overview", ""], ["Introduction", ""]], desc["top"], head_extra=legacy_home)
    home["title"] = ""

    groups = method["groups"]
    body = [SEC(None, "lede"), {"b": "mtoc", "items": [{"u": f"#{g['id']}", "t": f"{i}. {g['h']}"} for i, g in enumerate(groups, 1)]},
            P(method["lede"])]
    for i, g in enumerate(groups, 1):
        body.append(SEC(f"{i}. {g['h']}", g["id"]))
        for it in g["items"]:
            related = links(it["links"], xref)
            body += [H3(it["name"], en=it.get("en", "")), P(it["t"], mn=note("相关", links=related) if related else None)]
    n = sum(len(g["items"]) for g in groups)
    methodology = route("overview/methodology.html", "overview", "overview/methodology.html", "领域重要技术总览",
                        page("methodology", "领域重要技术总览", body, sub="Methodology", meta=[f"{len(groups)} 组 · {n} 项技术"], mtoc=True),
                        [["Overview", ""], ["Methodology", ""]], desc["methodology"])

    ledes = howto["group_ledes"]
    groups = [{"h": m["label"], "lede": ledes.get(m["key"], ""), "items": key_items([SECTION_KEY[u] for _, u in m["items"]], xref)} for m in NAV]
    body = [SEC(None, "intro"), P(howto["intro"]),
            SEC("站点结构", "sitemap"), TOC(groups),
            SEC("推荐阅读顺序", "order"), REFS([{"left": who, "k": k, "gloss": how} for who, k, how in howto["order"]]),
            SEC("页面上的标记", "markers"), UL([{"label": a, "t": b} for a, b in howto["markers"]]),
            SEC("关于本站：调研方法与核查说明", "method"), P(meta.get("method_zh"))]
    howto_r = route("overview/how-to-use.html", "overview", "overview/how-to-use.html", "如何使用本站",
                    page("howto", "如何使用本站", body, sub="How to use"), [["Overview", ""], ["How to use", ""]], desc["howto"])
    return [home, methodology, howto_r]


def site_routes(ctx, xref, legacy_home):
    parts = [overview_routes(ctx, xref, legacy_home), routes_routes(ctx, xref), foundations_routes(ctx, xref), advanced_routes(ctx, xref),
             classics_routes(ctx, xref), glossary_route(ctx, xref), papers_routes(ctx, xref), walkthrough_routes(ctx, xref),
             fieldmap_route(ctx, xref), areas_routes(ctx, xref), ideas_routes(ctx, xref), trends_route(ctx, xref)]
    routes = [r for part in parts for r in part]
    # Section front pages chain prev / next in navigation order.
    fronts = {r["path"]: r for r in routes}
    order = [fronts[u] for _, _, u in SECTIONS if u in fronts]
    for i, r in enumerate(order):
        if i > 0:
            r["series"].setdefault("prev", order[i - 1]["page"]["id"])
        if i + 1 < len(order):
            r["series"].setdefault("next", order[i + 1]["page"]["id"])
    for r in routes:
        r["page"]["head"]["minutes"] = read_minutes(r["page"]["body"])
        r["page"]["series"] = {k: ({"k": v} if isinstance(v, str) else v) for k, v in r["series"].items()}
        r["refs"] = refs_of(r["page"], xref) | refs_of(r.get("extra", {}), xref)
    return routes


# ---------- old urls ----------
def old_page_of(key: str) -> str | None:
    for page_, ids in OLD_SECTIONS.items():
        if key in ids:
            return page_
    for pre, page_ in OLD_PREFIX:
        if key.startswith(pre):
            return page_
    return None


def legacy_map(xref) -> dict:
    """Old page file -> {old element id: new url}; "" holds the page's default target."""
    out = {p: {"": xref[OLD_SECTIONS[p][0]]["u"]} for p in OLD_SECTIONS}
    for key, x in xref.items():
        p = old_page_of(key)
        if p:
            out[p][key] = x["u"]
    return out
