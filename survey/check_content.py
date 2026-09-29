"""Content check: every piece of text of the old 11-page site must appear somewhere in the new site.

Usage:
  python3 check_content.py --save .baseline     # dump the current top-level site/*.html pages into .baseline/ (before a redesign)
  python3 check_content.py .baseline            # compare the new site against that reference
  python3 check_content.py .baseline --all      # also list whitelisted fragments

The old pages are split into text fragments (text nodes, cut at " — " / " · " separators). A fragment counts as
present when its normalized form occurs in the normalized text of some new page. Normalizing drops whitespace,
colons, dashes, middle dots, parentheses and TeX, lowercases Latin text, and (for the old text) writes concept /
topic ids the way the new pages show them (as names). Side and margin notes are compared as their own text so
that a note floated into a paragraph does not split it. Fragments that were navigation or controls of the old
pages are whitelisted below, each with the reason. The old text goes through the same wording rules as the build
(wording.py), and the check fails if "锚点" is left anywhere on a page outside its technical uses.
"""
import os
import re
import signal
import subprocess
import sys
import tempfile
from collections import Counter, defaultdict
from concurrent.futures import ThreadPoolExecutor
from html.parser import HTMLParser
from pathlib import Path

import wording
from chrome import chrome_cmd

HERE = Path(__file__).resolve().parent
SITE = HERE / "site"
SKIP = {"script", "style", "nav", "mjx-container", "title", "noscript"}
VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "source", "track", "wbr"}
NOTE_CLASSES = {"sidenote", "marginnote", "mtoc"}
TEX = re.compile(r"\\\((?:.|\n)*?\\\)|\\\[(?:.|\n)*?\\\]")
SEPARATORS = re.compile(r"\s+[—–·|]\s+|^[—–·|]\s+|\s+[—–·|]$")
DROP = re.compile(r"[\s:：·—–|()（）↗→›▸‹←…]+")
ID_TOKEN = re.compile(r"(a-[a-z0-9]+(?:-[a-z0-9]+)*|[fgdrilnv]-[a-z0-9]+)")

# Old-site text that belonged to navigation, controls or page chrome rather than content: (reason, exact texts or a
# regex on the raw fragment). Everything else of the old site must appear in the new one.
WHITELIST = [
    ("old counters and filter results", r"^\d+ / \d+ (条|篇)$|^（\d+ / \d+）$"),
    ("rounded citation counts; the exact count and its source are shown", r"^引用 [\d.]+k$"),
    ("old file names in the site map", r"^[a-z]+\.html$"),
    ("old English eyebrows (the navigation is English now)", [
        "Field survey & study guide", "3D telepresence / real-time 3D vision", "Executive summary", "Method & caveats",
        "Site map", "Part I", "Part II", "Part III", "Learn", "Survey", "Research", "Roadmap", "Paradigms", "Research opportunities",
        "Sub-areas", "Anchor papers", "Guided reading", "Pre-2026 classics", "Reading list", "Advanced topics", "Glossary",
        "Foundations", "Field map", "Trends & challenges", "Paper database"]),
    ("old section headings, replaced by the new page titles", [
        "基础知识：读懂这个领域需要的 40 个概念", "进阶专题与奠基论文", "2026 年之前的高影响论文", "学习路线：从零到能复现两篇锚点论文",
        "研究机会：经对抗查新与评审的方向", "两篇锚点论文精读（研究视角）", "精读导读：用基础知识读懂两篇锚点论文", "分方向综述",
        "论文 / 产品 / 标准库", "跨方向趋势与重大挑战", "执行摘要", "调研方法与使用说明", "内容导航", "端到端技术栈全景",
        "表示与渲染范式对比"]),
    ("old Chinese site name; the site is now called 3D Telepresence: a field guide", ["3D 临场研究图谱"]),
    ("old navigation groups and page names", [
        "领域调研", "入门学习", "研究", "研究机会", "分方向与论文库", "方法与说明", "本页下方", "概览", "锚点论文", "领域全景",
        "精读导读", "学习路线", "基础知识", "进阶专题", "经典论文", "术语表"]),
    ("old block labels, renamed in the new layout (companion pages, margin notes)", [
        "流程图（点击方框跳到对应步骤）", "怎么读实验部分", "张量形状追踪", "逐步拆解", "新手常问", "延伸专题", "延伸到进阶专题",
        "前置概念", "前置", "与两篇锚点论文的联系", "与两篇锚点论文的关系", "在两篇锚点论文中"]),
    ("per-concept usage pills; the same fact heads each concept's 案例 section", r"^(Quark|Ha) (用到|未用)$"),
    ("old buttons and filter controls (the classics list is now split into theme pages)", [
        "按引用数", "按年份", "只看必读", "全部难度", "全部主题", "全部", "打开论文 ↗", "查看本方向论文 →", "前往精读导读 →"]),
    ("old home hero and start cards; the Introduction replaces them (P3)", [
        "领域论文 / 产品 / 标准", "2026 年前高影响论文", "经查新评审的研究方向", "基础概念", "零基础", "从学习路线开始",
        "分阶段的概念、论文、课程和动手项目", "想读懂两篇论文", "逐步拆解 Quark 与 Ha et al.，每一步链接到所需的基础概念",
        "找研究方向", "18 个经对抗查新与模拟评审的方向", "锚点 A · Quark (SIGGRAPH Asia 2024)", "锚点 B · Ha et al. (CVPR 2025)"]),
    ("old ledes and page descriptions rewritten for the new structure in P3 (new text: data/site/overview.json)",
     r"^(按 6 个主题收录 2025 年及以前发表的高影响论文。|8 个模块按学习顺序排列。每个概念都有|把两篇论文按流水线拆成若干步。|"
     r"这些方向来自 5 个独立视角|面向刚进入 3D 视觉 / 临场方向的研究生|以两篇锚点论文为坐标原点)"
     r"|^把 Quark（\d+ 步）和 Ha et al\.（\d+ 步）逐步拆开，每一步链接到所需的基础概念。$"
     r"|^8 个模块、40 个概念：直觉、公式、例子、易错点，以及在两篇锚点论文中的位置。$"
     r"|^8 个阶段：每阶段的概念、论文、课程、动手项目和检查题，最后复现两篇锚点论文。$"),
    ("old page descriptions and ledes about the old page structure; rewritten for the new pages (P3 reviews them)", [
        "全站按“入门学习 / 领域调研 / 研究”三部分组织。左侧（手机上为顶部）导航栏可随时切换页面，每页底部有上一页 / 下一页。",
        "全站概览、执行摘要、内容导航与调研方法。", "调研流程、核查方式与使用注意事项（位于概览页底部）。",
        "152 篇 2026 年前的高影响论文（时间分布图 + 可筛选列表），以及前沿阅读清单。",
        "两篇锚点论文的研究视角精读：精确数字、设计选择、局限与谱系，以及两者的对比与互补。",
        "端到端技术栈全景、表示与渲染范式对比、跨方向趋势与重大挑战。",
        "10 个子方向的综述，以及 359 条可筛选的论文 / 产品 / 标准库。",
        "偏研究者视角的精读：精确数字、设计选择、局限与谱系。想从零读懂，请先看入门学习部分的“精读导读”页。",
        "每个方向包含演进脉络、子主题、时间线、趋势与开放问题。点“查看本方向论文”跳到论文库并按方向筛选。",
        "读论文时遇到的缩写和术语。点右侧概念可跳到对应的基础知识卡片。"]),
]


def normalize(s: str) -> str:
    return DROP.sub("", TEX.sub("", s)).lower()


class TextNodes(HTMLParser):
    """Text nodes of a page; with `split_notes`, the text of side / margin notes goes to a separate stream."""

    def __init__(self, split_notes=False):
        super().__init__()
        self.split_notes = split_notes
        self.stack, self.skip, self.note = [], 0, 0
        self.out, self.notes = [], []

    def handle_starttag(self, tag, attrs):
        if tag in VOID:
            return
        cls = set((dict(attrs).get("class") or "").split())
        s, n = tag in SKIP, self.split_notes and bool(cls & NOTE_CLASSES)
        self.stack.append((s, n))
        self.skip += s
        self.note += n

    def handle_endtag(self, tag):
        if tag in VOID or not self.stack:
            return
        s, n = self.stack.pop()
        self.skip -= s
        self.note -= n

    def handle_data(self, data):
        if self.skip:
            return
        for part in TEX.split(data):
            t = re.sub(r"\s+", " ", part).strip()
            if t:
                (self.notes if self.note else self.out).append(t)


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
    """Every page of the site except redirect pages (old urls), which Chrome would follow to a page counted anyway."""
    return sorted(p for p in SITE.rglob("*.html")
                  if not p.name.startswith(".") and '<meta name="robots" content="noindex">' not in p.read_text(encoding="utf-8")[:600])


def id_names() -> dict:
    """Concept / topic id -> the label the new pages show for it in prose."""
    sys.path.insert(0, str(HERE))
    import build  # noqa: E402  (standard library only)
    learn = build.build_learn({})
    names = {c["id"]: c["name_zh"].split("：")[0] for m in learn.get("modules", []) for c in m["concepts"]}
    names.update({t["id"]: t["title_zh"] for t in learn.get("advanced", [])})
    return names


def with_names(s: str, names: dict) -> str:
    def sub(m):
        i, a, b = m.group(1), m.start(), m.end()
        prev, nxt = s[a - 1:a], s[b:b + 1]
        if i in names and not re.match(r"[A-Za-z0-9_\-]", prev) and not re.match(r"[A-Za-z0-9_]", nxt):
            return names[i]
        return i
    return ID_TOKEN.sub(sub, s)


def fragments(node: str):
    for f in SEPARATORS.split(node):
        f = f.strip()
        if f:
            yield f


def main() -> int:
    args = sys.argv[1:]
    if len(args) == 2 and args[0] == "--save":
        out = Path(args[1])
        out.mkdir(parents=True, exist_ok=True)
        for p in sorted(SITE.glob("*.html")):
            (out / p.name).write_text(dump(p), encoding="utf-8")
            print("saved", out / p.name)
        return 0
    show_all = "--all" in args
    args = [a for a in args if a != "--all"]
    if len(args) != 1:
        print(__doc__)
        return 2
    src = Path(args[0])
    names = id_names()

    with ThreadPoolExecutor(max_workers=6) as ex:
        doms = list(ex.map(lambda p: (p, dump(p)), site_pages()))
    corpus, wording_left = [], []
    for page, html in doms:
        t = TextNodes(split_notes=True)
        t.feed(html)
        corpus += [normalize(" ".join(t.out)), normalize(" ".join(t.notes))]
        wording_left += [(page.relative_to(SITE).as_posix(), c) for c in wording.leftovers("".join(t.out + t.notes))]
    corpus = "\x00".join(corpus)

    missing, allowed, total = defaultdict(Counter), defaultdict(Counter), 0
    for f in (sorted(src.glob("*.html")) if src.is_dir() else [src]):
        for node, n in texts(f.read_text(encoding="utf-8", errors="replace")).items():
            for frag in fragments(node):
                key = normalize(with_names(wording.apply(frag), names))
                if len(key) < 2:
                    continue
                total += n
                if key in corpus:
                    continue
                reason = next((r for r, pat in WHITELIST
                               if (frag in pat if isinstance(pat, list) else re.search(pat, frag))), None)
                (allowed if reason else missing)[f.name][frag] += n
    n_missing = sum(sum(c.values()) for c in missing.values())
    n_allowed = sum(sum(c.values()) for c in allowed.values())
    print(f"old fragments {total}; present {total - n_missing - n_allowed}; whitelisted {n_allowed}; MISSING {n_missing}")
    for page in sorted(set(missing) | set(allowed)):
        m = missing.get(page, Counter())
        if m:
            print(f"\n{page}: {sum(m.values())} missing")
            for k, v in sorted(m.items(), key=lambda x: -len(x[0])):
                print(f"  - {v}x {k[:160]}")
        if show_all and allowed.get(page):
            print(f"\n{page}: whitelisted")
            for k, v in allowed[page].items():
                print(f"  = {v}x {k[:120]}")
    # Wording: "锚点" may only remain where it is a technical term (wording.TECHNICAL).
    print(f"\nwording: {len(wording_left)} non-technical 锚点 left on pages")
    for page, c in wording_left[:40]:
        print(f"  ! {page}: …{c}…")
    return 1 if n_missing or wording_left else 0


if __name__ == "__main__":
    sys.exit(main())
