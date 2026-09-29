"""Display-layer wording rules (docs/redesign-tufte.md 5.1): the site no longer centres on two "anchor" papers, so
phrases such as "两篇锚点论文" are shown as "两篇重点论文". The data files keep their original wording; build.py
applies the rules to every string before rendering, and check_content.py applies them to the old pages before
comparing. "锚点" is also a technical term (Quark's equal-disparity layer anchors, Scaffold-GS anchors, anchor
baselines), and those uses stay: TECHNICAL lists them, and check_content.py reports any other "锚点" left on a page.
Standard library only.
"""
import re

# (pattern, replacement), applied in order.
RULES = [
    (r"两篇锚点论文", "两篇重点论文"),
    (r"两篇锚点", "两篇重点论文"),
    (r"锚点论文", "重点论文"),
    (r"锚点(深读|笔记|资料|方法|网络)", r"重点论文\1"),
    (r"锚点 ([AB])(?![A-Za-z])", r"重点论文 \1"),
    (r"以 Quark 为核心锚点", "以重点论文 Quark 为核心"),
    (r"第二个锚点 Ha", "第二篇重点论文 Ha"),
    (r"本章锚点：", "本章重点论文："),
    (r"与锚点(?=的联系|的关系|的关键|对照|没有|有两处)", "与重点论文"),
    (r"落在锚点的前提", "落在重点论文的前提"),
    (r"见锚点(?= lineage)", "见重点论文"),
    (r"(对|读|读懂|理解|看清|审视|标出|放宽|见|回到|适用于)锚点(?=[^驱运加之属特结位为上密激高投取半在和，。（）±\s])", r"\1重点论文"),
    (r"锚点(?=之后|对应位置|本身|后继|的路线|自己的|方向上|的适用|的一个已知|用网络|没有使用|的取舍|放弃|的 Q|读者)", "重点论文"),
]
_RULES = [(re.compile(p), r) for p, r in RULES]

# Technical uses of 锚点 that stay as they are (matched on the text around each occurrence).
TECHNICAL = re.compile(
    r"(等视差|深度|公制|三个|静止的|如果|层的?|第 ℓ 层|LDM |邻近|自己的|多偏离|偏离|直接取|就是|即|个|条件|激活|多级|残差|继承|"
    r"自适应的|感知的|时间|空间|可泛化的|无序|少量|存|对|建模|GS |Scaffold-GS 的|Scaffold-GS 用|提供|在|用|或|标记、|作为|"
    r"Starline |码率控制|传输格式|LPIPS |EMA |稳定|为)锚点"
    r"|锚点(深度|驱动|运动|加小|之上|之间|属性|特征|结构|位置|为编码|上下文|密度|激活|高斯|投影|取 δ|半个|在归一|和 M|，把|（anchor|）|。|，|±|只覆盖|细节|纳入|：DS|以限制|的 F)")


def apply(s: str) -> str:
    if "锚点" not in s:
        return s
    for pat, rep in _RULES:
        s = pat.sub(rep, s)
    return s


def apply_all(obj):
    """The same data with every string reworded (dict keys untouched)."""
    if isinstance(obj, str):
        return apply(obj)
    if isinstance(obj, list):
        return [apply_all(x) for x in obj]
    if isinstance(obj, dict):
        return {k: apply_all(v) for k, v in obj.items()}
    return obj


def leftovers(text: str, width: int = 12):
    """Occurrences of 锚点 in `text` that are not a known technical use, with some context."""
    out = []
    for m in re.finditer("锚点", text):
        window = text[max(0, m.start() - 14):m.end() + 12]
        if not TECHNICAL.search(window):
            out.append(text[max(0, m.start() - width):m.end() + width].replace("\n", " "))
    return out
