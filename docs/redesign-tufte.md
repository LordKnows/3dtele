# 3D 临场学习站改版：主题选型与 Tufte 改版计划

- 日期：2026-09-29
- 分支：`worktree-tufte-redesign`（基于 `origin/main` d78071e）
- 范围：`survey/`（构建脚本、页面渲染、样式）；线上站点为 https://3dv.zyhu.dev
- 状态：**选型已定，计划已确认，尚未动手改站点代码**

---

## 1. 这一阶段做了什么

1. 调研了 13 个技术博客 / 知识库主题，分成三类：学术长文、技术博客、文档/知识库。每个主题都用 headless Chrome 截了真实 demo（首页、文章页浅色、文章页深色），并按本站需求逐项评估。
2. 做了一个对比页 `theme-gallery/index.html`，截图放在 `theme-gallery/shots/`，截图脚本是 `theme-gallery/shoot.py`，要截的地址列在 `theme-gallery/urls.txt`。
3. 用户选定 **#3 Tufte CSS** 的形式，并提出了改版的四点要求（见第 2 节）。
4. 本文档记录选型结论、确认过的决定和改版计划。

查看对比页的方法：

```bash
python3 -m http.server 8765 --bind 127.0.0.1 --directory theme-gallery
```

然后打开 http://localhost:8765/ 。

### 1.1 候选与结论

| # | 主题 | 类别 | 框架 | 结论 |
|---|---|---|---|---|
| 1 | Distill | 学术长文 | HTML + Web Components | 旁注和悬停引用可以参考；模板 2022 年起停更 |
| 2 | al-folio | 学术长文 | Jekyll | 更适合个人学术主页 |
| **3** | **Tufte CSS** | 学术长文 | 纯 CSS | **选定**：旁注、边注、书籍版式，可以直接借到现有构建里 |
| 4 | Quarto | 学术长文 | Pandoc | 迁移路线的首选；这次不迁移 |
| 5 | PaperMod（Lil'Log） | 技术博客 | Hugo | 阅读版式好，没有侧栏导航 |
| 6 | Blowfish | 技术博客 | Hugo + Tailwind | 风格偏花哨 |
| 7 | Stack | 技术博客 | Hugo | 中文生态好，卡片风格偏生活博客 |
| 8 | Fuwari | 技术博客 | Astro | 二次元风，维护慢 |
| 9 | Material → Zensical | 文档 | MkDocs / Rust | Material 2025-11 起维护模式；Zensical 还是 0.0.x |
| 10 | Starlight | 文档 | Astro | 迁移路线里最灵活；公式要自己配 |
| 11 | VitePress | 文档 | Vue | 内置搜索默认搜不到中文词 |
| 12 | Hextra | 文档 | Hugo | 迁移路线里依赖最轻 |
| 13 | Hugo Book | 文档 | Hugo | 朴素的“书”式章节树 |

**路线**：走“换皮 + 重组”，不迁移框架。保留 `survey/build.py`（只用标准库，部署流程依赖这一点）、JSON 数据和 JS 渲染代码，重写信息结构、页面粒度和样式。

---

## 2. 用户确认的决定

| # | 决定 |
|---|---|
| D1 | 版式采用 **Tufte CSS** 的形式。西文完全沿用 Tufte（ET Book）。 |
| D2 | 中文字体：**正文用思源宋体（Noto Serif SC），旁注、边注和副标题用霞鹜文楷（LXGW WenKai）**。对应关系是“西文斜体 ↔ 中文楷体”，也呼应古籍批注用楷体的传统。 |
| D3 | 不再以 Quark 和 Ha 为锚点。两篇降为“重点论文”，整站改成面向 **整个 3D 临场领域** 的学习网站。 |
| D4 | 导航改为**横向、全英文、4 个模块**，每个模块带下拉菜单（见第 3 节）。 |
| D5 | 每个概念、每个专题、每篇精读都写成独立的博客式页面，参考 Tufte 版式。 |
| D6 | 保留现有便于理解的交互，但换成适合 Tufte 的设计。 |
| D7 | **内容全部保留**，只改布局和排列，减少单页内容量。 |
| D8 | 首页执行摘要重写为领域导览；原文不删，移到 Works › Papers 下面。 |

---

## 3. 信息结构

### 3.1 导航

```
Overview      Basics              Works          Future
              ├ Routes            ├ Papers       ├ Directions*
              ├ Foundations       ├ Walkthrough  └ Trends & Challenges*
              ├ Advanced topics   ├ Field map
              ├ Classics          └ Sub areas
              └ Glossary
```

\* 标了星号的条目是我的提议，用户还没确认。Overview 暂定为单页，下拉里放页内锚点：Introduction / How to use / Methodology。

### 3.2 各模块内容与现有内容的对应

| 导航 | 内容 | 来源（现有） | 大约页数 |
|---|---|---|---|
| **Overview** | 领域导览（新写）、本站怎么用、方法与说明 | `home.js`、`meta.json` | 1 |
| Basics › **Routes** | 学习路线总览 + 8 个阶段各一篇 | `roadmap` | 1 + 8 |
| Basics › **Foundations** | 总览 → 8 个模块页（M1–M8）→ 40 篇概念 | `foundations` | 1 + 8 + 40 |
| Basics › **Advanced topics** | 总览 + 16 篇专题 | `advanced` | 1 + 16 |
| Basics › **Classics** | 总览（时间线 + 必读清单）+ 6 个主题各一篇 | `classics` | 1 + 6 |
| Basics › **Glossary** | 195 条术语，可搜索 | `glossary` | 1 |
| Works › **Papers** | 重点论文：Quark 精读、Ha 精读、两者对比；调研摘要（原执行摘要）；论文库（359 条，可筛选） | `anchors`、`synth.executive_summary_zh`、`areas.papers` | 约 5 |
| Works › **Walkthrough** | Quark 导读、Ha 导读，每篇按流水线阶段拆成约 3 篇 | `guided` | 约 6 |
| Works › **Field map** | 端到端技术栈全景 + 表示与渲染范式对比 | `landscape` 的 `map`、`paradigms` | 1–2 |
| Works › **Sub areas** | 总览 + 10 个子方向各一篇 | `areas` | 1 + 10 |
| **Future** | 研究方向总览（排行）+ 18 篇方向；趋势、重大挑战、1–3 年判断 | `ideas`、`landscape` 的 `trends` | 1 + 18 + 1 |

合计约 **130 页**（现在是 11 页）。按现有数据估算单页篇幅：概念约 8–11k 字符，专题约 18k，子方向约 12k，研究方向约 13k，都适合一篇一页。导读每篇约 70k，必须拆开。

### 3.3 网址

- 网址用英文 slug，按目录分层。例如：`basics/foundations/g-pinhole.html`、`works/walkthrough/quark-1.html`、`future/C02.html`。
- 所有站内链接按页面深度生成**相对路径**，这样本地 `file://` 和线上都能用。线上 Cloudflare 的 `html_handling: auto-trailing-slash` 会把 `x.html` 映射成 `/x`，目录的 `index.html` 映射成 `/dir/`，相对路径两种情况都成立。
- **旧网址保留跳转**：`roadmap.html`、`foundations.html#concept-…` 等旧文件改成跳转页，按 `#锚点` 映射到新地址。`index.html` 本身是新首页，里面加一小段脚本，识别旧锚点再跳转。
- `survey/telepresence-atlas.html` 这个跳转页继续保留。

---

## 4. 版式规范（Tufte + 中文）

### 4.1 页面结构

- **顶栏**：细横向导航，英文小型大写字母，下拉菜单。条目多的下拉分栏；手机端收成汉堡菜单，里面是折叠列表。
- **标题区**：面包屑；H1 是中文标题，下面用 ET Book 斜体写英文名，比如“对极几何 *Epipolar geometry*”。
- **元信息**：所属模块、阅读时间、前置知识。前置知识放在边注里。
- **题记**：用一句话 TL;DR（`tldr_zh`）做 Tufte 式的 epigraph。
- **正文**：约 55% 宽的窄栏。右侧页边放编号旁注（sidenote）和不编号边注（marginnote）。大图、大表用通栏（`fullwidth`）。
- **文末**：自测（答案可以展开）、延伸阅读、同系列上一篇 / 下一篇。
- **手机端**：旁注收成可点击展开的符号（Tufte 的 ⊕ 模式）。

### 4.2 字体与排印

| 用途 | 西文 | 中文 |
|---|---|---|
| 正文、标题 | ET Book | 思源宋体（Noto Serif SC）400 / 600 |
| 副标题、旁注、边注、题记、图注 | ET Book Italic | 霞鹜文楷（LXGW WenKai） |
| 代码、数字标签 | IBM Plex Mono（沿用） | — |

- 正文字号约 18–19px，行高约 1.85，一行约 38 个汉字。
- 中西文之间留间距（`text-autospace`，不支持时回退），标点做挤压（`halt`）。
- 配色沿用 Tufte：浅色底 `#fffff8`、墨色字，只保留一个强调色用于交互。深色模式保留，包括跟随系统和手动切换。
- 字体加载：思源宋体用 Google Fonts（现有做法，按字符分片加载）；霞鹜文楷用 jsDelivr 上的 `lxgw-wenkai-webfont`，固定版本号；ET Book 从 tufte-css 自托管（MIT 许可）。**构建脚本仍然只用标准库**，不在构建时做字体子集化。

### 4.3 现有交互怎么改

| 现有 | 改成 |
|---|---|
| “类比”框、提示框（`asideBox`） | 边注 |
| 前置知识标签 | 文首的边注：“阅读前需要：…” |
| 相关论文、专题标签 | 正文里的旁注引用 + 文末“延伸阅读” |
| 页内概念链接（`refChip` / `rich`） | 保留，改成行内链接；**可选**：鼠标悬停时弹出一句话定义 |
| 折叠卡片（`details`） | 页面变短后正文不再折叠；只有自测答案和很长的可选内容保留折叠 |
| Quark/Ha 标签页（`makeTabs`） | 拆成独立的文章 |
| 导读流水线图（SVG，节点可点击） | 通栏图，改成素墨加一个强调色；点节点仍然跳到对应步骤（跨页时跳到对应分篇） |
| 经典论文时间线（SVG，悬停和筛选） | 放在 Classics 总览的通栏图里；每个主题页放一张小时间线 |
| 论文库、术语表的搜索和筛选 | 保留；表格改成三线表，输入框改成下划线样式 |
| 成熟度条、评分条 | Tufte 式的小图表（●●●○○、迷你条形、数字表） |
| 卡片网格（趋势、挑战等） | 改成带编号的段落 |
| 左侧栏目录 | 去掉。长文的目录放在页边顶部，其余靠顶栏导航、面包屑和上一篇/下一篇 |

---

## 5. 去锚点化

- **概念页调整顺序**，先讲领域层面，再讲案例：直觉 → 公式 → 例子 → 易错点 → **在 3D 临场系统中** → **案例：Quark 与 Ha 如何使用**（`in_quark` / `in_ha`）。
- **专题和子方向**：`relation_to_anchors_zh` 改为文末的“与重点论文的关系”一节。
- **经典论文**：`anchor_link_zh` 改成旁注。
- **学习路线**：最后一个阶段保留，改名为结业项目“复现两篇重点论文”。
- **措辞**：数据里的“锚点”一共出现 452 次。在构建的显示层统一替换为“重点论文”一类说法，源数据不改，可以回退；替换规则单独列表并加检查。
- **重写**：首页导语、各页导语、页面描述（`page_desc`）、`meta.json` 里以锚点为中心的说法。
- **执行摘要**：约 1,900 字的原文完整保留到 Works › Papers › 调研摘要；Overview 另写一篇领域导览。

---

## 6. 技术方案

- **构建**：`build.py` 里的 `PAGES` 改成路由表。一篇文章对应一条路由：`{route, template, data slice, nav 位置, 上一篇/下一篇}`。每页只嵌入自己用到的数据。
- **跨页链接**：现在的 `PREFIX_PAGE`（id 前缀映射到页面）改成 **id → 网址 + 标题 + 一句话简介** 的完整映射，大约 300 个条目。它同时给悬停预览用。
- **渲染**：继续在浏览器端渲染，复用 `core.js` 里的 `el`、`rich`、`eqList`、`typeset`。页面脚本改成按“文章类型”组织：`concept`、`module`、`topic`、`classic-theme`、`paper`、`walkthrough`、`area`、`idea`、`stage` 等，再加上几个工具页（论文库、术语表）。
- **外壳**：`shell.html` 改成顶栏加 Tufte 文章骨架；`styles.css` 重写。
- **安全**：沿用现有做法——`safeUrl` 只放行 https，DOM 一律用 `textContent` 构建，JSON 用 `</` 转义后嵌入。外部资源固定版本号。

### 6.1 检查

| 检查 | 内容 |
|---|---|
| `check_content.py`（扩展） | **内容完整**：旧站 DOM 里的每一段文字都要在新站某一页出现（显示层的措辞替换除外，按规则表比对） |
| 新增链接检查 | 每个站内 `href` 都指向存在的页面；每个 `#id` 都存在；每条旧网址都能跳到新地址 |
| `check_render.py` | 公式没有残留原始 TeX，页面没有空白区块 |
| `check_layout.py` | 390px 和 1400px 下没有横向溢出；旁注在窄屏折叠；下拉菜单能用键盘操作 |

---

## 7. 阶段与验收

| 阶段 | 做什么 | 给用户看什么 / 验收标准 |
|---|---|---|
| **P0 样张** | 做一篇真实的概念页（例如“对极几何”）：顶栏和下拉、Tufte 版式、字体、旁注、公式、深色模式、手机端 | 用户确认版式和字体 |
| **P1 骨架** | 路由表、网址工具、导航数据、文章模板、旧网址跳转、链接检查 | 所有路由都能生成页面，链接检查通过 |
| **P2 转换** | 按顺序：概念 → 模块页 → 专题 → 经典论文 → 学习路线 → 术语表 → 重点论文 → 导读 → 全景 → 子方向 → 论文库 → 研究方向 | 每一类转完就跑内容完整检查 |
| **P3 首页** | 写 Overview 领域导览，处理执行摘要，重写导语 | 用户审阅新写的文字 |
| **P4 收尾** | 全量检查、清理旧样式；经用户同意后推送分支，拿到 Cloudflare 预览地址 | 预览站点验收后再合并到 `main`，合并即上线 |

---

## 8. 待确认与风险

**待确认**

1. Overview 是做成单页（下拉只放页内锚点），还是也拆成子页？
2. Future 下拉里的 Directions、Trends & Challenges 这两个条目。
3. 导读每篇拆成几部分？默认按流水线阶段拆 3 部分。
4. 是否要做链接悬停预览？默认会做，放在 P2 末尾。

**风险**

- **中文网页字体体积**：思源宋体和霞鹜文楷都要按字符分片加载，首屏可能先用系统字体、再切换（FOUT）。需要用 `font-display: swap` 并在 P0 实测。
- **旁注在中文长段落里的对齐**：Tufte 的旁注依赖浮动布局，中文段落很长时旁注之间可能重叠。P0 要验证。
- **页数从 11 页变成约 130 页**：每页都内联 `core.js` 加页面脚本，单页体积可以接受。以后可以考虑把公共脚本抽成独立文件。
- **线上网址变化**：旧网址靠跳转页兜底，外部已有的链接不会失效。

---

## 附：参考资料

- Tufte CSS — https://edwardtufte.github.io/tufte-css/ （MIT）
- Material for MkDocs 进入维护模式 / Zensical — https://squidfunk.github.io/mkdocs-material/blog/2025/11/05/zensical/
- VitePress 中文分词问题 — https://github.com/vuejs/vitepress/issues/4049
- Quarto 文章版式 — https://quarto.org/docs/authoring/article-layout.html
- 霞鹜文楷 — https://github.com/lxgw/LxgwWenKai
- 思源宋体 / Noto Serif SC — https://fonts.google.com/noto/specimen/Noto+Serif+SC
