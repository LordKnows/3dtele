# 3D 临场学习站改版：主题选型与 Tufte 改版计划

- 日期：2026-09-29（第 2 版：用户已回答全部待确认问题）
- 分支：`worktree-tufte-redesign`，基于 `origin/main` d78071e；worktree 路径 `.claude/worktrees/tufte-redesign`
- 范围：`survey/`（构建脚本、页面渲染、样式、检查脚本）；线上站点 https://3dv.zyhu.dev
- 状态：**选型和计划已全部确认，还没有开始改站点代码**。下一步从 P0 开始（见第 8 节）。
- 执行方：另一个 Claude Code session 会按本文档执行。**请先读第 9 节“给执行 session 的说明”。**

---

## 1. 这一阶段做了什么

1. 调研了 13 个技术博客 / 知识库主题，分成学术长文、技术博客、文档/知识库三类。每个主题都用 headless Chrome 截了真实 demo（首页、文章页浅色、文章页深色），并按本站需求逐项评估。
2. 做了一个对比页：`theme-gallery/index.html`。截图在 `theme-gallery/shots/`，截图脚本是 `theme-gallery/shoot.py`，要截的地址列在 `theme-gallery/urls.txt`。
3. 用户选定 **#3 Tufte CSS** 的形式，提出改版要求，并回答了全部待确认问题（见第 2 节）。

查看对比页：

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

**路线**：走“换皮 + 重组”，不迁移框架。保留 `survey/build.py`（只用标准库，部署依赖这一点）、JSON 数据和 JS 渲染代码，重写信息结构、页面粒度和样式。

---

## 2. 用户确认的决定

| # | 决定 |
|---|---|
| D1 | 版式采用 **Tufte CSS** 的形式。西文完全沿用 Tufte（ET Book）。 |
| D2 | 中文字体：**正文用思源宋体（Noto Serif SC），旁注、边注和副标题用霞鹜文楷（LXGW WenKai）**。对应关系是“西文斜体 ↔ 中文楷体”，也呼应古籍批注用楷体的传统。 |
| D3 | 不再以 Quark 和 Ha 为锚点。两篇降为“重点论文”，整站改成面向 **整个 3D 临场领域** 的学习网站。 |
| D4 | 导航改为**横向、全英文、4 个模块**，每个模块都有下拉菜单（见第 3 节）。 |
| D5 | 每个概念、每个专题、每篇精读都写成独立的博客式页面，参考 Tufte 版式。 |
| D6 | 保留现有便于理解的交互，但换成适合 Tufte 的设计。 |
| D7 | **内容全部保留**，只改布局和排列，减少单页内容量。 |
| D8 | 首页执行摘要重写为领域导览；原文不删，移到 Works › Papers 下面。 |
| D9 | Overview 带下拉，分 Introduction / Methodology / How to use 三页。**Methodology 写成“领域重要技术总览”**：总结这个领域的重要技术，并逐一介绍（见 5.2）。 |
| D10 | Future 下拉：Directions、Trends & Challenges。 |
| D11 | **每篇论文的导读做成一篇长文**；导读里可以独立成篇的部分（张量追踪、阅读实验、设计权衡、FAQ、练习、论文术语）**各自单独成篇**（见 3.2）。 |
| D12 | 要做**链接悬停预览**：鼠标移到站内概念、专题、论文链接上时，弹出一句话简介。 |

---

## 3. 信息结构

### 3.1 导航

```
Overview           Basics              Works          Future
├ Introduction     ├ Routes            ├ Papers       ├ Directions
├ Methodology      ├ Foundations       ├ Walkthrough  └ Trends & Challenges
└ How to use       ├ Advanced topics   ├ Field map
                   ├ Classics          └ Sub areas
                   └ Glossary
```

- 导航文字全部用英文；页面正文仍是中文。
- 下拉条目多的时候分栏，但下拉只到二级（上图这一层）。三级内容（比如 40 个概念）放在各二级的索引页里列出，不塞进下拉。
- 手机端收成汉堡菜单，里面是折叠列表。

### 3.2 各模块内容与现有内容的对应

| 导航 | 内容 | 来源（现有） | 大约页数 |
|---|---|---|---|
| Overview › **Introduction** | 站点首页：领域导览（**新写**），以及从哪里开始学 | 新写；参考 `synth.executive_summary_zh` 和 `field_map` | 1 |
| Overview › **Methodology** | 领域重要技术总览（**新写**，见 5.2） | 新写；素材来自 `field_map`、`paradigms`、`advanced`、`modules` | 1 |
| Overview › **How to use** | 本站结构、推荐阅读顺序；文末附“关于本站：调研方法与核查说明”（**原“方法与说明”全文移到这里**） | `meta.json` 里的 `method_zh` 和 `learn_method_zh`；`home.js` 里的 sitemap | 1 |
| Basics › **Routes** | 学习路线总览 + 8 个阶段各一篇 | `roadmap` | 1 + 8 |
| Basics › **Foundations** | 总览 → 8 个模块页（M1–M8）→ 40 篇概念 | `modules` | 1 + 8 + 40 |
| Basics › **Advanced topics** | 总览 + 16 篇专题 | `advanced` | 1 + 16 |
| Basics › **Classics** | 总览（时间线 + 必读清单 + 前沿阅读清单 `reading_path`）+ 6 个主题各一篇 | `classics`、`themes`、`reading_path` | 1 + 6 |
| Basics › **Glossary** | 全站术语表，约 195 条，可搜索 | `glossary` | 1 |
| Works › **Papers** | 总览；Quark 精读；Ha 精读；两者对比；调研摘要（原执行摘要全文）；论文库（359 条，可筛选） | `anchors.quark`、`anchors.ha`、`anchors.compare`、`synth.executive_summary_zh`、`papers` | 1 + 5 |
| Works › **Walkthrough** | 总览；每篇论文一篇**导读长文**，外加 6 篇配套（见下） | `guided.quark`、`guided.ha` | 1 + 2 × 7 |
| Works › **Field map** | 端到端技术栈全景 + 表示与渲染范式对比，合成一篇 | `synth.field_map`、`synth.paradigms` | 1 |
| Works › **Sub areas** | 总览 + 10 个子方向各一篇 | `areas`，不含 `works` 字段；论文条目进论文库 | 1 + 10 |
| Future › **Directions** | 总览（18 个方向的排行和评分）+ 18 篇方向 | `ideas` | 1 + 18 |
| Future › **Trends & Challenges** | 跨方向趋势、重大挑战、1–3 年判断，合成一篇 | `synth.trends_zh`、`grand_challenges_zh`、`predictions_zh` | 1 |

合计约 **150 页**（现在是 11 页）。

**导读怎么拆（D11）**

| 篇目 | 字段 | 篇幅（Quark / Ha，字符数） |
|---|---|---|
| 导读长文 | `story_zh` + `before_you_read` + 流水线图 + `walkthrough` 全部步骤（Quark 12 步，Ha 14 步） | 约 41k / 41k |
| 张量追踪 | `tensor_trace` | 3.2k / 2.3k |
| 阅读实验 | `reading_experiments` | 3.3k / 3.4k |
| 设计权衡 | `tradeoffs` | 1.7k / 1.2k |
| 常见问题 | `faq` | 3.3k / 2.6k |
| 练习 | `exercises` | 4.4k / 4.3k |
| 论文术语 | 导读里的 `glossary` | 4.1k / 4.0k |

- 导读长文开头要有一个页边目录，列出全部步骤；流水线图的节点点击后跳到对应步骤。
- 长文结尾列出这 6 篇配套文章。
- 每篇配套文章的开头都链接回导读长文。

### 3.3 网址

- 网址用英文 slug，按目录分层。例如：
  - `index.html`（Introduction）、`overview/methodology.html`、`overview/how-to-use.html`
  - `basics/routes/index.html`、`basics/routes/stage-1.html`
  - `basics/foundations/index.html`、`basics/foundations/m2.html`、`basics/foundations/g-pinhole.html`
  - `basics/advanced/a-geo-fm.html`、`basics/classics/t-neural-rendering.html`、`basics/glossary.html`
  - `works/papers/quark.html`、`works/papers/ha.html`、`works/papers/compare.html`、`works/papers/summary.html`、`works/papers/database.html`
  - `works/walkthrough/quark.html`、`works/walkthrough/quark-tensor-trace.html`（其余配套同理：`-experiments`、`-tradeoffs`、`-faq`、`-exercises`、`-glossary`）
  - `works/field-map.html`、`works/areas/rt-nvs.html`
  - `future/index.html`、`future/C02.html`、`future/trends.html`
- 所有站内链接按页面深度生成**相对路径**，这样本地 `file://` 和线上都能用。线上 Cloudflare 的 `html_handling: auto-trailing-slash` 会把 `x.html` 映射成 `/x`，目录的 `index.html` 映射成 `/dir/`，相对路径两种情况都成立。
- **旧网址保留跳转**：`roadmap.html`、`foundations.html`、`guided.html`、`advanced.html`、`classics.html`、`glossary.html`、`anchors.html`、`landscape.html`、`areas.html`、`ideas.html` 改成跳转页，按 `#锚点` 映射到新地址。例如 `foundations.html#concept-g-pinhole` 跳到 `basics/foundations/g-pinhole.html`，`guided.html#walk-ha-h3` 跳到 `works/walkthrough/ha.html#walk-ha-h3`。
- `index.html` 本身是新首页，里面加一小段脚本，识别旧锚点（`#summary`、`#sitemap`、`#method` 等）再跳转。
- `survey/telepresence-atlas.html` 继续作为跳转页，映射表改成指向新地址。
- 旧的元素 id（`concept-…`、`walk-…`、`classic-…`、`idea-…` 等）在新页面里继续保留，这样跳转后的锚点仍然有效。

---

## 4. 版式规范（Tufte + 中文）

### 4.1 页面结构

- **顶栏**：细横向导航，英文小型大写字母，带下拉菜单。当前所在模块高亮。浅色 / 深色切换按钮放在顶栏右侧。
- **标题区**：面包屑；H1 是中文标题，下面用 ET Book 斜体写英文名，比如“对极几何 *Epipolar geometry*”。
- **元信息**：所属模块、预计阅读时间（按约 500 字/分钟估算）、前置知识。前置知识放在边注里。
- **题记**：用一句话 TL;DR（`tldr_zh`）做 Tufte 式的 epigraph。
- **正文**：约 55% 宽的窄栏。右侧页边放编号旁注（sidenote）和不编号边注（marginnote）。大图、大表用通栏（`fullwidth`）。
- **文末**：自测（答案可以展开）、延伸阅读、同系列上一篇 / 下一篇。
- **手机端**：旁注收成可点击展开的符号（Tufte 的 ⊕ 模式）。
- **索引页**（各二级总览，比如 Foundations 总览）：不用卡片网格，改成 Tufte 式的目录列表——标题、一行简介、篇幅，按模块或主题分组。

### 4.2 字体与排印

| 用途 | 西文 | 中文 |
|---|---|---|
| 正文、标题 | ET Book | 思源宋体（Noto Serif SC）400 / 600 |
| 副标题、旁注、边注、题记、图注 | ET Book Italic | 霞鹜文楷（LXGW WenKai） |
| 导航 | ET Book 小型大写 | — |
| 代码、数字标签 | IBM Plex Mono（沿用） | — |

- 正文字号约 18–19px，行高约 1.85，一行约 38 个汉字。
- 中西文之间留间距（`text-autospace`，不支持时回退），标点做挤压（`halt`）。
- 配色沿用 Tufte：浅色底 `#fffff8`、墨色字，只保留一个强调色用于交互。深色模式保留，包括跟随系统和手动切换。
- 字体加载：
  - 思源宋体用 Google Fonts，沿用现在 `shell.html` 的做法，按字符分片加载。
  - 霞鹜文楷用 jsDelivr 上的 `lxgw-wenkai-webfont`，固定版本号。
  - ET Book 从 tufte-css 仓库自托管（MIT 许可），woff 文件提交到 `survey/site/fonts/`，同时附上许可证。
  - **构建脚本仍然只用标准库**，不在构建时做字体子集化。
  - 所有字体都用 `font-display: swap`。

### 4.3 现有交互怎么改

| 现有 | 改成 |
|---|---|
| “类比”框、提示框（`asideBox`） | 边注 |
| 前置知识标签 | 文首的边注：“阅读前需要：…” |
| 相关论文、专题标签 | 正文里的旁注引用 + 文末“延伸阅读” |
| 页内概念链接（`refChip` / `rich`） | 行内链接 + **悬停预览**（见 4.4） |
| 折叠卡片（`details`） | 页面变短后正文不再折叠；只有自测答案和很长的可选内容保留折叠 |
| Quark/Ha 标签页（`makeTabs`） | 拆成独立的文章 |
| 导读流水线图（SVG，节点可点击） | 放在导读长文开头，做成通栏图；改成素墨加一个强调色；点节点跳到同页对应步骤 |
| 经典论文时间线（SVG，悬停和筛选） | 放在 Classics 总览的通栏图里；每个主题页放一张只含本主题论文的小时间线 |
| 论文库、术语表的搜索和筛选 | 保留；表格改成三线表，输入框改成下划线样式 |
| 成熟度条、评分条 | Tufte 式的小图表（●●●○○、迷你条形、数字表） |
| 卡片网格（趋势、挑战、首页入口等） | 改成带编号的段落或目录列表 |
| 左侧栏目录 | 去掉。长文的目录放在页边顶部，其余靠顶栏导航、面包屑和上一篇/下一篇 |

### 4.4 链接悬停预览（D12）

- 覆盖所有站内链接到的条目：概念、模块、专题、经典论文、重点论文、导读步骤、子方向、研究方向、术语。
- 预览内容：标题（中文 + 英文名）、所属模块、一句话简介。简介优先取 `tldr_zh`；没有的话，取正文第一句并截断到约 80 字。
- 数据来源：构建时生成的 **id → {网址, 标题, 英文名, 模块, 简介}** 映射。每页只嵌入本页实际链接到的那些条目，不嵌入全表。
- 交互：鼠标悬停约 300ms 后出现，移开后消失；键盘 focus 也会触发；按 Esc 关闭。触屏上不弹预览，直接跳转。
- 样式：霞鹜文楷小字、细边框、无阴影，符合 Tufte 的克制风格。
- 安全：预览里的内容一律用 `textContent` 写入。

---

## 5. 内容调整

### 5.1 去锚点化

- **概念页调整顺序**，先讲领域层面，再讲案例：直觉 → 公式 → 例子 → 易错点 → **在 3D 临场系统中**（`in_field_zh`）→ **案例：Quark 与 Ha 如何使用**（`in_quark` / `in_ha`）。
- **专题和子方向**：`relation_to_anchors_zh` 改为文末的“与重点论文的关系”一节。
- **经典论文**：`anchor_link_zh` 改成旁注。
- **学习路线**：最后一个阶段保留，改名为结业项目“复现两篇重点论文”。
- **措辞**：数据里“锚点”一共出现 452 次，页面脚本里还有若干处。
  - 在构建的显示层统一替换，源数据不改，可以回退。
  - 替换规则写成一张表（比如“两篇锚点论文”→“两篇重点论文”，“锚点论文”→“重点论文”，“锚点 A/B”→“重点论文 A/B”）。
  - 替换后另加一项检查：页面里不应再出现“锚点”二字。
- **重写**：各页导语、页面描述（`page_desc`）、`meta.json` 里以锚点为中心的说法。
- **执行摘要**：约 1,900 字的原文**完整保留**到 Works › Papers › 调研摘要。

### 5.2 需要新写的内容

新写的文字统一放在 `survey/data/site/overview.json`（新文件），不要混进已有的数据文件。所有新文字都要在 P3 交给用户审阅。

**Introduction（首页领域导览）**

- 3D 临场要解决什么问题。
- 技术栈从采集到显示分几层，每层一两句话，链接到 Field map。
- 当前进展、主要难点和几条主线趋势。
- 按读者类型给出三条起步路径：
  - 新手 → Routes
  - 有基础 → Advanced topics / Sub areas
  - 找研究题目 → Future
- 两篇重点论文只作为“代表系统”提一句，链接到 Works › Papers。
- 篇幅约 1,500–2,500 字。

**Methodology（领域重要技术总览，D9）**

- 目标：用一页讲清这个领域的重要技术。每项技术写：它是什么、解决什么问题、主要方法和代表工作、现在的局限，并链接到对应的 Foundations 概念、Advanced topic 和 Sub area。
- 建议按技术栈组织，每组 1–3 项技术，每项 150–300 字：
  1. 采集与标定（多相机阵列、RGB-D 传感器、标定与同步）
  2. 深度与几何估计（立体匹配、MVS、单目深度、前馈几何基础模型）
  3. 场景与人体表示（MPI / 分层表示、点云与网格、TSDF、NeRF、3D Gaussian Splatting、4D 表示）
  4. 渲染与新视角合成（IBR 与混合、体渲染、光栅化 / splatting、可泛化与前馈渲染、无几何 Transformer 渲染）
  5. 生成先验与补全（扩散模型、新视角生成）
  6. 动态与时间一致性（动态重建、流式重建、视频时间一致性）
  7. 压缩与传输（体积视频编码、神经表示压缩、延迟）
  8. 显示与交互（光场 / 裸眼 3D 显示、视线与感知）
  9. 评测（图像指标、时间指标、感知与用户研究）
- 素材只能来自站内已有的内容：`synth.field_map`、`synth.paradigms`、`advanced`（16 个专题）、`modules`（8 个模块）、`areas`。**不要引入站内没有、也没有核实过的新事实或新数字。**
- 开头写一段导语，说明这一页和 Field map 的分工：Field map 讲“技术栈每层的成熟度和瓶颈”，Methodology 讲“有哪些关键技术、各是什么”。
- 篇幅约 4,000–6,000 字。

**How to use**

- 站点结构、推荐阅读顺序、页面上各种标记是什么意思（旁注、悬停预览、自测）。
- 文末附“关于本站：调研方法与核查说明”：`method_zh` 和 `learn_method_zh` 的原文全部保留。

---

## 6. 技术方案

- **构建**：`build.py` 里的 `PAGES` 改成路由表。一篇文章对应一条路由：`{route, template, data slice, nav 位置, 上一篇/下一篇}`。每页只嵌入自己用到的数据。
- **跨页链接**：现在的 `PREFIX_PAGE`（id 前缀映射到页面）改成 **id → 网址** 的完整映射；悬停预览用同一份映射（见 4.4）。
- **渲染**：继续在浏览器端渲染，复用 `core.js` 里的 `el`、`rich`、`eqList`、`typeset`、`safeUrl`。页面脚本按“文章类型”组织：
  - 文章类：`intro`、`methodology`、`howto`、`stage`、`concept`、`module`、`topic`、`classic-theme`、`paper`、`compare`、`summary`、`walkthrough`、`walk-part`、`fieldmap`、`area`、`idea`、`trends`
  - 索引页：各二级总览
  - 工具页：论文库、术语表
- **外壳**：`shell.html` 改成顶栏加 Tufte 文章骨架；`styles.css` 重写。
- **安全**：沿用现有做法——`safeUrl` 只放行 https，DOM 一律用 `textContent` 构建，JSON 用 `</` 转义后嵌入。外部资源固定版本号。

### 6.1 检查

| 检查 | 内容 |
|---|---|
| `check_content.py`（改造） | **内容完整**：旧站 11 页 DOM 里的每一段文字，都要在新站某一页出现。按措辞替换规则表比对，删掉的导航和按钮文字列为白名单 |
| 新增 `check_links.py` | 每个站内 `href` 都指向存在的文件；每个 `#id` 都存在；每条旧网址（旧页面 + 旧锚点）都能跳到存在的新地址；每个悬停预览条目都有简介 |
| `check_render.py`（改造） | 改为递归扫描 `site/**/*.html`；公式没有残留原始 TeX；没有控制台报错；页面没有空白区块 |
| `check_layout.py`（改造） | 递归扫描；390px 和 1400px 下没有横向溢出；旁注在窄屏折叠；下拉菜单能用键盘操作；深链接（新网址 + `#id`）落点正确 |
| 措辞检查 | 页面上不再出现“锚点” |

---

## 7. 已知风险

- **中文网页字体体积**：思源宋体和霞鹜文楷都要按字符分片加载，首屏可能先显示系统字体再切换（FOUT）。P0 要实测首屏效果。
- **旁注在中文长段落里的对齐**：Tufte 的旁注依赖浮动布局，中文段落很长时旁注之间可能重叠。P0 要验证；必要时限制每段的旁注数量，或者改成按段落对齐。
- **页数从 11 页变成约 150 页**：每页都内联 `core.js` 加页面脚本，单页体积可以接受。以后可以把公共脚本抽成独立的 `.js` 文件。
- **线上网址变化**：旧网址靠跳转页兜底，外部已有的链接不会失效。
- **导读长文约 4 万字**：必须有页边目录和步骤锚点，否则很难读。

---

## 8. 阶段与验收

每个阶段结束都要在分支上提交一次，并把截图或本地预览地址给用户看。

| 阶段 | 做什么 | 验收 |
|---|---|---|
| **P0 样张** | 先生成改版前的基线（见 9.3）。然后做一篇真实的概念页“对极几何”（`g-epipolar`），包括：顶栏和全部下拉（链接可以先是占位）、Tufte 版式、两种中文字体、旁注和边注、公式、悬停预览、深色模式、手机端 | 用户确认版式、字体和悬停预览 |
| **P1 骨架** | 路由表、网址工具、导航数据、id → 网址映射、文章模板、各二级索引页、旧网址跳转、`check_links.py` | 所有路由都能生成页面，链接检查通过 |
| **P2 转换** | 按顺序：概念 → 模块页 → 专题 → 经典论文 → 学习路线 → 术语表 → 重点论文（精读、对比、调研摘要）→ 导读长文和配套 → Field map → 子方向 → 论文库 → 研究方向 → Trends & Challenges | 每转完一类就跑内容完整检查和链接检查 |
| **P3 新写内容** | Introduction、Methodology、How to use；各页导语；措辞替换规则 | 用户审阅新写的文字 |
| **P4 收尾** | 全量检查；删掉旧样式和旧页面脚本；更新 `telepresence-atlas.html` 跳转；**经用户同意后**推送分支，拿到 Cloudflare 预览地址 | 预览站点验收后再合并到 `main`，合并即上线 |

---

## 9. 给执行 session 的说明

### 9.1 工作环境

- 在 worktree **`/Users/ZhongyuanHu/research/3dtele/.claude/worktrees/tufte-redesign`**（分支 `worktree-tufte-redesign`）里工作。如果 session 是从主仓库启动的，先用 EnterWorktree 并传 `path` 切进这个 worktree。
- 用中文和用户交流。
- 每个阶段结束都要提交。提交信息用英文，末尾加上 session 要求的 Co-Authored-By 行。
- `survey/site/` 下的构建产物是纳入 git 的，改完要重新构建并一起提交。
- **推送必须先得到用户同意**：推送任何分支都会触发 Cloudflare 预览部署，推送到 `main` 就直接上线。

### 9.2 关键文件

| 文件 | 作用 |
|---|---|
| `survey/build.py` | 汇总数据、校验交叉链接、生成 `survey/site/`。**只能用 Python 标准库** |
| `survey/assemble.py` | 把 `data/learn/drafts/` 和 `data/learn/final/` 合并成 `data/learn/content.json`（`final` 优先）。这次改版一般不需要重跑 |
| `survey/data/survey.json` | `anchors`（quark / ha / compare）、`areas`（10 个子方向，每个约 45 条 `works`）、`synth`（执行摘要、全景、范式、趋势、挑战、预测、阅读路径） |
| `survey/data/learn/content.json` | `foundations`、`advanced`、`classics`、`guided`、`roadmap`、`glossary` |
| `survey/data/learn/skeleton.json` | 概念 id（`f-`/`g-`/`d-`/`r-`/`i-`/`l-`/`n-`/`v-` 前缀）、专题 id（`a-*`）、经典论文主题（`t-*`）。所有交叉链接都用这些 id |
| `survey/data/review.json` + `ideas_zh.json` | 18 个研究方向 |
| `survey/meta.json` | 页面导语、`method_zh`、`learn_method_zh` |
| `survey/src/shell.html`、`styles.css`、`core.js`、`pages/*.js` | 外壳、样式、公共函数、各页渲染代码。`build.py` 把 core 和页面脚本拼成一个 IIFE 内联进每页 |
| `wrangler.jsonc`、`.github/workflows/deploy.yml` | Cloudflare 部署：CI 会运行 `python survey/build.py`，然后发布 `survey/site` |

### 9.3 构建与检查

```bash
python3 survey/build.py
python3 survey/check_render.py
python3 survey/check_layout.py
```

- **基线**：P0 **动手之前**，先用当前代码构建一次，再用 headless Chrome `--dump-dom` 把旧站 11 页的 DOM 分别存到 `survey/.baseline/`（加进 `.gitignore`）。`check_content.py` 改成接受这个目录，把 11 页合起来作为参照。
- headless Chrome 的路径是 `/Applications/Google Chrome.app/Contents/MacOS/Google Chrome`。它的子进程可能卡住管道，所以要把 stdout 写到文件，用 `start_new_session=True` 启动，超时后用 `os.killpg` 结束。现有检查脚本都是这么写的，照着来。
- headless Chrome 的窗口宽度不能小于约 500px。手机宽度用 iframe 模拟，参考 `check_layout.py` 的做法。
- `theme-gallery/shoot.py` 可以批量截图，环境变量 `WS=宽,高`，每行第三列写 `light` / `dark` 强制配色。

### 9.4 本地预览

- 内置浏览器的一键预览只读主仓库根目录的 `.claude/launch.json`，而隔离在 worktree 里的 session 写不了主仓库。
- 所以在 worktree 里直接起服务器：

  ```bash
  python3 -m http.server 8766 --bind 127.0.0.1 --directory survey/site
  ```

  再用内置浏览器打开 `http://localhost:8766/`。
- 用 `file://` 直接打开时，内置浏览器会把页面当静态快照加载，图片等相对路径资源可能加载不出来。

### 9.5 约束

- 内容一字不删（D7）。措辞替换只在显示层做。新写的文字放在 `survey/data/site/overview.json`。
- 不引入构建依赖。前端外部资源只有 Google Fonts、jsDelivr（`lxgw-wenkai-webfont`、MathJax 3.2.2），都固定版本。
- 遵守用户全局的安全编码规则：DOM 用 `textContent`、只放行 https 链接、JSON 嵌入要转义、不用 `eval` 或 `innerHTML` 拼接不可信内容。

---

## 附：参考资料

- Tufte CSS — https://edwardtufte.github.io/tufte-css/ （MIT；ET Book 字体在仓库的 `et-book/` 目录）
- Material for MkDocs 进入维护模式 / Zensical — https://squidfunk.github.io/mkdocs-material/blog/2025/11/05/zensical/
- VitePress 中文分词问题 — https://github.com/vuejs/vitepress/issues/4049
- Quarto 文章版式 — https://quarto.org/docs/authoring/article-layout.html
- 霞鹜文楷 — https://github.com/lxgw/LxgwWenKai
- 思源宋体 / Noto Serif SC — https://fonts.google.com/noto/specimen/Noto+Serif+SC
