"""Combine learning-content drafts and reviewed results into data/learn/content.json.

Reviewed / verified files (in data/learn/final) take precedence over drafts (data/learn/drafts).
"""
import json
import re
import sys
from pathlib import Path

LEARN = Path(__file__).resolve().parent / "data" / "learn"
DRAFTS, FINAL = LEARN / "drafts", LEARN / "final"


def load(p: Path):
    with p.open(encoding="utf-8") as f:
        return json.load(f)


def pick(*names):
    """Return the first existing file among final/ then drafts/ for each candidate name."""
    for n in names:
        for d in (FINAL, DRAFTS):
            p = d / n
            if p.exists():
                return load(p), f"{d.name}/{n}"
    return None, None


def norm_title(t: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", (t or "").lower())[:60]


def merge_classics(sweeps):
    by = {}
    for papers in sweeps:
        for p in papers:
            k = norm_title(p.get("title"))
            if not k:
                continue
            prev = by.get(k)
            if prev is None:
                by[k] = {**p, "themes": [p.get("theme")]}
                continue
            if p.get("theme") not in prev["themes"]:
                prev["themes"].append(p.get("theme"))
            if (p.get("citations") or -1) > (prev.get("citations") or -1):
                prev["citations"], prev["citations_source"] = p["citations"], p.get("citations_source")
            if len(p.get("influence_zh", "")) > len(prev.get("influence_zh", "")):
                prev["influence_zh"] = p["influence_zh"]
            prev["concept_ids"] = list(dict.fromkeys((prev.get("concept_ids") or []) + (p.get("concept_ids") or [])))
            prev["must_read"] = bool(prev.get("must_read") or p.get("must_read"))
    return list(by.values())


def main() -> int:
    sk = load(LEARN / "skeleton.json")
    out, sources = {}, {}

    out["foundations"] = []
    for m in sk["modules"]:
        mod, src = pick(f"review_{m['id']}.json", f"write_{m['id']}.json")
        if mod:
            mod["module_id"] = m["id"]
            out["foundations"].append(mod)
            sources[m["id"]] = src

    out["advanced"] = []
    for i in range(5):
        g, src = pick(f"review_adv{i}.json", f"write_adv{i}.json")
        if g:
            out["advanced"].append(g)
            sources[f"adv{i}"] = src

    verified = FINAL / "classics_verified.json"
    if verified.exists():
        out["classics"] = load(verified)
        sources["classics"] = "final/classics_verified.json"
    else:
        sweeps = []
        for t in sk["classic_themes"]:
            s, src = pick(f"classics_{t['id']}.json")
            if s:
                sweeps.append(s["papers"])
                sources[t["id"]] = src
        out["classics"] = [{**p, "theme": p["themes"][0], "status": "unverified"} for p in merge_classics(sweeps)]

    out["guided"] = []
    for k in ("quark", "ha"):
        g, src = pick(f"verify_{k}.json", f"guide_{k}.json")
        if g:
            g["anchor"] = k
            out["guided"].append(g)
            sources[f"guide_{k}"] = src

    rm, src = pick("roadmap.json")
    out["roadmap"] = rm or {}
    if src:
        sources["roadmap"] = src
    gl, src = pick("glossary.json")
    out["glossary"] = gl or {"terms": []}
    if src:
        sources["glossary"] = src

    (LEARN / "content.json").write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    for k, v in sources.items():
        print(f"{k:22s} <- {v}")
    print(f"classics merged: {len(out['classics'])}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
