"""Assemble survey, idea-review and learning data, validate cross-links, and inject into the page template."""
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


def main() -> int:
    survey, areas, papers = build_survey()
    ideas = build_ideas()
    stats: dict = {}
    learn = build_learn(stats)
    meta = load_json(ROOT / "meta.json")
    if stats:
        meta["method_zh"] = meta["method_zh"] + "\n\n" + meta.get("learn_method_zh", "").format(**stats)
    data = {"meta": meta, "synth": survey.get("synth") or {}, "anchors": survey.get("anchors") or {},
            "areas": areas, "papers": papers, "ideas": ideas, "learn": learn}
    blob = json.dumps(data, ensure_ascii=False)
    # Keep the JSON inert inside <script type="application/json">.
    blob = blob.replace("</", "<\\/").replace("<!--", "<\\u0021--")
    tpl = (ROOT / "template.html").read_text(encoding="utf-8")
    if "/*__DATA__*/" not in tpl:
        print("placeholder missing", file=sys.stderr)
        return 1
    out = ROOT / "telepresence-atlas.html"
    out.write_text(tpl.replace("/*__DATA__*/", blob), encoding="utf-8")
    json.loads(re.search(r'id="data">(.*?)</script>', out.read_text(encoding="utf-8"), re.S).group(1))
    print(f"papers={len(papers)} areas={len(areas)} ideas={len(ideas)} stats={stats} bytes={out.stat().st_size}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
