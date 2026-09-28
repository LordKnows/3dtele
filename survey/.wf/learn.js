export const meta = {
  name: 'telepresence-learning-content',
  description: 'Write & verify learning content for the survey page: foundations (8 modules), advanced topics, pre-2026 classic papers, guided walkthroughs of Quark and Ha et al., then roadmap + glossary',
  phases: [
    { title: 'Foundations', detail: 'write each module, then technical edit + fact check' },
    { title: 'Advanced', detail: 'write advanced topics with foundational papers, then review' },
    { title: 'Classics', detail: 'thematic sweeps with citation counts, dedupe, batch verification' },
    { title: 'Guided', detail: 'step-by-step walkthroughs of both anchors, adversarially verified against the papers' },
    { title: 'Roadmap', detail: 'learning roadmap and glossary built on everything above' },
  ],
}

const SK = args
const D = '/Users/ZhongyuanHu/research/3dtele/survey/data'
const ALL_CONCEPTS = SK.modules.flatMap(m => m.concepts.map(c => ({ id: c.id, name_zh: c.name_zh, module: m.id })))
const CONCEPT_IDS = ALL_CONCEPTS.map(c => c.id)
const ADV_IDS = SK.advanced_topics.map(t => t.id)
const conceptIndex = ALL_CONCEPTS.map(c => `${c.id} = ${c.name_zh}`).join('\n')

const CONTEXT = `We are extending a Chinese-language web survey of 3D telepresence / real-time 3D vision. It is anchored on two papers:
(A) Quark: Real-time, High-resolution, and General Neural View Synthesis (Flynn et al., Google, SIGGRAPH Asia 2024) — https://arxiv.org/html/2411.16680v1
(B) Geometry-guided Online 3D Video Synthesis with Multi-View Temporal Consistency (Ha et al., KAIST + Meta, CVPR 2025) — https://arxiv.org/html/2505.18932v1
Verified Chinese deep-reads of both are at ${D}/anchor_quark.json and ${D}/anchor_ha.json (exact numbers, pipeline stages, design choices); a comparison is at ${D}/anchor_compare.json; an English critical deep-read of Ha et al. is at ${D}/deepread.md. The fixed curriculum skeleton is at ${D}/learn/skeleton.json.
READER: a new graduate student entering 3D vision / telepresence who knows undergraduate linear algebra, probability, Python and basic deep learning, but not multi-view geometry, rendering or neural rendering. The user wants the page to (1) teach the foundations, (2) teach advanced topics with foundational papers, (3) list influential pre-2026 papers, and (4) tie the foundations tightly to the two anchor papers so they become easy to understand.
WRITING RULES: Write all prose in fluent Simplified Chinese (keep standard English terms such as NeRF, 3DGS, TSDF, MPI, LDM, IBR, splatting, feed-forward, attention, and keep paper titles in English). Intuition first, then formula, then a concrete numeric or visual example. Explain every symbol of every formula. Be concrete and technical, no filler or marketing tone. Always say precisely where a concept appears in Quark and/or Ha et al. (section / pipeline stage / exact numbers) and what would be confusing without it.
MATH: put key formulas in equations[].tex as plain LaTeX WITHOUT $ or \\[ delimiters (MathJax renders them). In prose you may use inline math as \\( ... \\) sparingly.
LINKS & FACTS: Today is 2026-09-28. Use WebSearch/WebFetch (load via ToolSearch "select:WebSearch,WebFetch") and curl in Bash. Every URL you output must be real (opened, or seen in a search/API result). Prefer free resources: Szeliski "Computer Vision: Algorithms and Applications" 2nd ed (https://szeliski.org/Book/), PBRT online (https://pbr-book.org/), Dive into Deep Learning (https://d2l.ai/), official course pages (e.g. CMU 16-385 / 16-825, Stanford CS231A, MIT 6.S980, TUM multi-view geometry, UCSD CSE 291), arXiv abs pages, official project pages, well-known tutorials. Never invent papers, numbers or URLs. For temp files use \`mktemp -d\`; never write into ${D}.
CROSS-LINKS: the ONLY valid concept ids are:\n${conceptIndex}\nThe only valid advanced-topic ids are: ${ADV_IDS.join(', ')}. Use exactly these ids when a field asks for concept_ids / prereqs.`

const S = { type: 'string' }
const SA = { type: 'array', items: S }
const EQ = { type: 'array', items: { type: 'object', properties: { tex: S, explain_zh: S }, required: ['tex', 'explain_zh'] } }
const RES = { type: 'array', items: { type: 'object', properties: { title: S, url: S, type: { type: 'string', enum: ['book', 'course', 'paper', 'tutorial', 'code', 'video', 'blog'] }, note_zh: S }, required: ['title', 'url', 'type', 'note_zh'] } }
const QA = { type: 'array', items: { type: 'object', properties: { q_zh: S, a_zh: S }, required: ['q_zh', 'a_zh'] } }
const USE = { type: 'object', properties: { used: { type: 'boolean' }, where: S, how_zh: S }, required: ['used', 'where', 'how_zh'] }

const CONCEPT = { type: 'object', properties: {
  id: S, name_zh: S, name_en: S,
  tldr_zh: { type: 'string', description: 'one sentence' },
  intuition_zh: { type: 'string', description: '2-4 paragraphs separated by blank lines; plain-language explanation' },
  analogy_zh: { type: 'string', description: 'a vivid analogy or mental picture' },
  equations: EQ,
  worked_example_zh: { type: 'string', description: 'concrete numeric or step-by-step example' },
  pitfalls_zh: SA,
  in_quark: USE, in_ha: USE,
  in_field_zh: { type: 'string', description: 'where else in the telepresence stack it matters' },
  resources: RES,
  self_check: QA,
  prereqs: SA,
}, required: ['id', 'name_zh', 'name_en', 'tldr_zh', 'intuition_zh', 'analogy_zh', 'equations', 'worked_example_zh', 'pitfalls_zh', 'in_quark', 'in_ha', 'in_field_zh', 'resources', 'self_check', 'prereqs'] }
const MODULE_SCHEMA = { type: 'object', properties: { module_id: S, intro_zh: S, study_tips_zh: S, concepts: { type: 'array', items: CONCEPT } }, required: ['module_id', 'intro_zh', 'study_tips_zh', 'concepts'] }
const MODULE_REVIEW_SCHEMA = { type: 'object', properties: { ...MODULE_SCHEMA.properties, change_log: SA }, required: [...MODULE_SCHEMA.required, 'change_log'] }

const PAPER = { type: 'object', properties: { title: S, authors: S, year: { type: 'number' }, venue: S, url: S, citations: { type: 'number', description: '-1 if unknown' }, role_zh: S, priority: { type: 'string', enum: ['must', 'should', 'optional'] } }, required: ['title', 'authors', 'year', 'venue', 'url', 'citations', 'role_zh', 'priority'] }
const TOPIC = { type: 'object', properties: {
  id: S, title_zh: S, title_en: S,
  overview_zh: { type: 'string', description: '3-5 paragraphs separated by blank lines: the problem, the core ideas, how the field evolved, state of the art' },
  key_ideas: { type: 'array', items: { type: 'object', properties: { name_zh: S, explain_zh: S }, required: ['name_zh', 'explain_zh'] } },
  equations: EQ,
  evolution: { type: 'array', items: { type: 'object', properties: { year: { type: 'number' }, milestone_zh: S }, required: ['year', 'milestone_zh'] } },
  papers: { type: 'array', items: PAPER, description: '6-12 foundational papers, most important first' },
  prereqs: SA,
  relation_to_anchors_zh: S,
  debates_zh: SA,
  open_questions_zh: SA,
  resources: RES,
}, required: ['id', 'title_zh', 'title_en', 'overview_zh', 'key_ideas', 'equations', 'evolution', 'papers', 'prereqs', 'relation_to_anchors_zh', 'debates_zh', 'open_questions_zh', 'resources'] }
const ADV_SCHEMA = { type: 'object', properties: { topics: { type: 'array', items: TOPIC } }, required: ['topics'] }
const ADV_REVIEW_SCHEMA = { type: 'object', properties: { topics: { type: 'array', items: TOPIC }, change_log: SA }, required: ['topics', 'change_log'] }

const CLASSIC = { type: 'object', properties: {
  title: S, authors: { type: 'string', description: 'first author et al. (org if notable)' }, year: { type: 'number' }, venue: S, url: S,
  citations: { type: 'number', description: 'citation count, -1 if unknown' }, citations_source: { type: 'string', enum: ['Semantic Scholar', 'OpenAlex', 'unknown'] },
  theme: S,
  influence_zh: { type: 'string', description: 'why it is influential: what changed in the field because of it' },
  contributions_zh: S,
  anchor_link_zh: { type: 'string', description: 'how it connects to Quark and/or Ha et al.; empty string if no direct link' },
  concept_ids: SA,
  difficulty: { type: 'string', enum: ['入门', '进阶', '专家'] },
  must_read: { type: 'boolean' },
}, required: ['title', 'authors', 'year', 'venue', 'url', 'citations', 'citations_source', 'theme', 'influence_zh', 'contributions_zh', 'anchor_link_zh', 'concept_ids', 'difficulty', 'must_read'] }
const CLASSIC_SCHEMA = { type: 'object', properties: { papers: { type: 'array', items: CLASSIC } }, required: ['papers'] }
const VERIFIED = { type: 'object', properties: { ...CLASSIC.properties, status: { type: 'string', enum: ['verified', 'corrected', 'removed'] }, verify_note: S }, required: [...CLASSIC.required, 'status', 'verify_note'] }
const VERIFY_SCHEMA = { type: 'object', properties: { papers: { type: 'array', items: VERIFIED } }, required: ['papers'] }

const STEP = { type: 'object', properties: {
  id: S, title_zh: S, paper_ref: { type: 'string', description: 'section / figure / equation / table numbers in the paper' },
  what_zh: { type: 'string', description: 'what this step does: inputs -> outputs' },
  plain_zh: { type: 'string', description: 'plain-language explanation, 1-3 paragraphs separated by blank lines, explicitly invoking the foundation concepts' },
  analogy_zh: S,
  equations: EQ,
  numbers_zh: { type: 'string', description: 'exact hyperparameters / sizes / timings for this step' },
  why_design_zh: { type: 'string', description: 'why the authors chose this, what alternative they rejected and why' },
  pitfalls_zh: { type: 'string', description: 'what readers typically misunderstand here' },
  concept_ids: SA,
  check_q_zh: S, check_a_zh: S,
}, required: ['id', 'title_zh', 'paper_ref', 'what_zh', 'plain_zh', 'analogy_zh', 'equations', 'numbers_zh', 'why_design_zh', 'pitfalls_zh', 'concept_ids', 'check_q_zh', 'check_a_zh'] }
const GUIDE_PROPS = {
  anchor: { type: 'string', enum: ['quark', 'ha'] },
  story_zh: { type: 'string', description: '3-5 paragraphs separated by blank lines: the problem, the key intuition, the solution, told as a story for a newcomer' },
  before_you_read: { type: 'array', items: { type: 'object', properties: { concept_id: S, why_zh: S }, required: ['concept_id', 'why_zh'] } },
  walkthrough: { type: 'array', items: STEP },
  tensor_trace: { type: 'array', items: { type: 'object', properties: { stage_zh: S, tensor: S, shape: S, note_zh: S }, required: ['stage_zh', 'tensor', 'shape', 'note_zh'] } },
  reading_experiments: { type: 'array', items: { type: 'object', properties: { item: S, how_to_read_zh: S, takeaway_zh: S }, required: ['item', 'how_to_read_zh', 'takeaway_zh'] } },
  tradeoffs: { type: 'array', items: { type: 'object', properties: { choice_zh: S, gain_zh: S, cost_zh: S }, required: ['choice_zh', 'gain_zh', 'cost_zh'] } },
  faq: QA,
  exercises: { type: 'array', items: { type: 'object', properties: { title_zh: S, level: { type: 'string', enum: ['入门', '进阶', '挑战'] }, task_zh: S, expected_zh: S, hint_zh: S, concept_ids: SA }, required: ['title_zh', 'level', 'task_zh', 'expected_zh', 'hint_zh', 'concept_ids'] } },
  glossary: { type: 'array', items: { type: 'object', properties: { term_en: S, term_zh: S, def_zh: S }, required: ['term_en', 'term_zh', 'def_zh'] } },
}
const GUIDE_SCHEMA = { type: 'object', properties: GUIDE_PROPS, required: Object.keys(GUIDE_PROPS) }
const GUIDE_VERIFY_SCHEMA = { type: 'object', properties: { ...GUIDE_PROPS, fixes: { type: 'array', items: { type: 'object', properties: { location: S, problem: S, fix: S, evidence: S }, required: ['location', 'problem', 'fix', 'evidence'] } } }, required: [...Object.keys(GUIDE_PROPS), 'fixes'] }

const QUARK_STEPS = `q1 问题设定与输入（M=8 个最近视角、近/远平面由 SfM 点估计）
q2 输入编码：残差 CNN 特征金字塔 + 射线方向编码 γ
q3 LDM 表示与深度参数化（等视差锚点、每层只能在自己的视差带内移动）
q4 学习式初始化（可学习特征广播 + back-projection 到锚定平面）
q5 Render：把当前 LDM 双线性 splat 到每个输入视角并 over 合成得到 Ĩ
q6 Update：比较 Ĩ 与观测特征，生成逐视角 update feature，再按当前深度反投影成 Δ
q7 Fuse：One-to-many attention 跨视角融合（含 W^K/W^V 折叠技巧）
q8 由粗到细：分辨率翻倍 + Layer Collapse（24 层 36×64 → 6 层 288×512）
q9 上采样后激活（post-activation，借鉴 ReLU Fields）
q10 IBR 混合与 over 合成：全分辨率输入像素的凸组合
q11 训练：数据混合、10·L1 + LPIPS、两阶段分辨率、学习率日程
q12 如何读实验、运行时间与消融`
const HA_STEPS = `h1 问题设定：固定标定同步阵列、K 个最近 RGB-D 视角、在线逐帧
h2 深度从哪来：RAFT-Stereo（人工选对）或深度传感器
h3 前向渲染：像素大小、各向同性、完全不透明的高斯，逐视角单独 splat 得到 I_k、α_k、D_k
h4 软差分掩码：M = min(|I_t − I_{t−1}|/λ_t + β, 1)，1/4 分辨率 + max-pool
h5 静止区域的时间深度滤波（EMA）
h6 基于图像的 TSDF：沿目标射线采样，投影到 K 个视角求 s_k = z_k − D_k
h7 截断与融合权重（τ = 0.02 m、基于 7×7 局部深度方差的权重）
h8 光线步进求零交叉 + 二分细化 → 一致的新视角深度
h9 时间反馈：上一帧新视角深度作为额外 TSDF 输入（ω_tmp、η = 15）
h10 几何引导混合网络的输入特征（9K+1 通道）
h11 混合输出：K 个逐像素权重 + 背景权重 + 背景图像
h12 损失：0.8·L1 + 0.2·SSIM + 0.1·L_depth + 0.1·L_mask
h13 训练数据、推理加速（TensorRT）与运行时间拆解
h14 如何读实验：PSNR/LPIPS vs TCC/STED/SDT/SDV、EPI、消融`

// ---------------- Branch A: foundations ----------------
const foundationsP = pipeline(
  SK.modules,
  m => agent(`${CONTEXT}\n\nTASK: Write foundation module ${m.id} "${m.title_zh}" (${m.title_en}). Goal: ${m.goal_zh}\nConcepts to write, in this order, keeping these exact ids and prereqs (you may refine the Chinese names slightly):\n${JSON.stringify(m.concepts, null, 1)}\n\nFor each concept produce: tldr, 2-4 paragraphs of intuition, an analogy, 1-4 key equations with term-by-term explanations (0 only if the concept is truly non-mathematical), a concrete worked example with numbers, 2-4 pitfalls, precise usage in Quark and in Ha et al. (read the anchor deep-read files, and fetch the paper HTML to confirm section numbers; set used=false with how_zh explaining the absence if a paper does not use it), where else it matters in telepresence, 2-4 real learning resources (book chapters with the chapter/section named, course lectures, tutorials, the original paper), and 2-3 self-check questions with answers. Also write a module intro (why this module matters for telepresence) and study tips (what to do by hand / in code to internalize it).`,
    { label: `write:${m.id}`, phase: 'Foundations', schema: MODULE_SCHEMA }),
  (draft, m) => agent(`${CONTEXT}\n\nYou are a rigorous TECHNICAL EDITOR and FACT-CHECKER. Below is a draft of foundation module ${m.id} "${m.title_zh}". Check every formula (signs, indices, conventions, units), every technical claim, every statement about Quark / Ha et al. (verify against ${D}/anchor_quark.json, ${D}/anchor_ha.json and, when in doubt, the paper HTML), and every URL (open it; replace dead or wrong links with real ones). Improve clarity for a newcomer: fill gaps in intuition, make worked examples concrete and numerically correct (recompute them), make sure pitfalls are real. Keep the exact concept ids and valid prereq ids. Return the corrected full module plus a change_log listing what you fixed.\n\nDRAFT:\n${JSON.stringify(draft)}`,
    { label: `review:${m.id}`, phase: 'Foundations', schema: MODULE_REVIEW_SCHEMA })
)

// ---------------- Branch B: advanced topics ----------------
const ADV_GROUPS = [
  SK.advanced_topics.filter(t => ['a-learned-stereo', 'a-learned-mvs', 'a-geo-fm'].includes(t.id)),
  SK.advanced_topics.filter(t => ['a-nerf-fast', 'a-3dgs-ext', 'a-diff-render'].includes(t.id)),
  SK.advanced_topics.filter(t => ['a-layered-nvs', 'a-generalizable-ibr', 'a-ff-3dgs', 'a-geometry-free'].includes(t.id)),
  SK.advanced_topics.filter(t => ['a-dynamic-4d', 'a-human-capture', 'a-temporal-video'].includes(t.id)),
  SK.advanced_topics.filter(t => ['a-diffusion-3d', 'a-telepresence-sys', 'a-compression'].includes(t.id)),
]
const advancedP = pipeline(
  ADV_GROUPS,
  g => agent(`${CONTEXT}\n\nTASK: Write these ADVANCED TOPICS (进阶专题) for the page, keeping the exact ids:\n${JSON.stringify(g, null, 1)}\n\nFor each topic: a 3-5 paragraph overview (problem, core ideas, evolution, state of the art as of 2026-09), 4-7 key ideas explained, 0-3 key equations with explanations, an evolution timeline, 6-12 foundational papers (most important first; title, first author et al., year, venue, real URL, Semantic Scholar citation count via https://api.semanticscholar.org/graph/v1/paper/search/match?query=...&fields=title,year,venue,citationCount or OpenAlex https://api.openalex.org/works?search=... ; use -1 if you cannot get it; what each introduced; priority must/should/optional), prereq concept ids, a precise relation to Quark and Ha et al., debates, open questions and 2-4 learning resources.`,
    { label: `write:adv${ADV_GROUPS.indexOf(g)}`, phase: 'Advanced', schema: ADV_SCHEMA }),
  (draft, g, i) => agent(`${CONTEXT}\n\nYou are a rigorous TECHNICAL EDITOR and FACT-CHECKER for these advanced-topic write-ups. Verify every paper (exists, correct year/venue/authors, URL opens, citation count plausible — re-query Semantic Scholar/OpenAlex for any that look off), every equation and technical claim, and every statement about Quark / Ha et al. (check ${D}/anchor_quark.json and ${D}/anchor_ha.json). Add any clearly missing foundational paper. Improve clarity for a newcomer. Keep ids. Return the corrected topics plus a change_log.\n\nDRAFT:\n${JSON.stringify(draft)}`,
    { label: `review:adv${i}`, phase: 'Advanced', schema: ADV_REVIEW_SCHEMA })
)

// ---------------- Branch C: classic papers ----------------
const classicsP = (async () => {
  const swept = await parallel(SK.classic_themes.map(t => () => agent(`${CONTEXT}\n\nTASK: Compile the most INFLUENTIAL papers published BEFORE 2026 (year <= 2025) for theme ${t.id} "${t.title_zh}". Scope hint (not exhaustive, not mandatory): ${t.scope}\nAim for 18-26 papers. Selection = high citation count and/or field-changing ideas, plus the classics a telepresence researcher must know, with extra weight on those that Quark and Ha et al. build on. For EACH paper get the citation count from Semantic Scholar (curl "https://api.semanticscholar.org/graph/v1/paper/search/match?query=<url-encoded title>&fields=title,year,venue,citationCount,externalIds"; on HTTP 429 wait a few seconds and retry) or from OpenAlex (curl "https://api.openalex.org/works?search=<title>&select=title,publication_year,cited_by_count,doi&per-page=3"); record which source. Give the canonical URL (arXiv abs, DOI, or official project/paper page). Set theme="${t.id}". Write why it is influential, its concrete contributions, its link to Quark/Ha (empty string if none), concept ids from the fixed list, difficulty and must_read (at most ~40% must_read).`,
    { label: `classics:${t.id}`, phase: 'Classics', schema: CLASSIC_SCHEMA })))
  const norm = s => String(s || '').toLowerCase().replace(/[^a-z0-9]+/g, '')
  const byKey = new Map()
  for (const r of swept.filter(Boolean)) for (const p of (r.papers || [])) {
    const k = norm(p.title).slice(0, 60)
    if (!k) continue
    const prev = byKey.get(k)
    if (!prev) byKey.set(k, { ...p, themes: [p.theme] })
    else {
      if (!prev.themes.includes(p.theme)) prev.themes.push(p.theme)
      if ((p.citations || -1) > (prev.citations || -1)) { prev.citations = p.citations; prev.citations_source = p.citations_source }
      if ((p.influence_zh || '').length > (prev.influence_zh || '').length) prev.influence_zh = p.influence_zh
      prev.concept_ids = [...new Set([...(prev.concept_ids || []), ...(p.concept_ids || [])])]
      prev.must_read = prev.must_read || p.must_read
    }
  }
  const merged = [...byKey.values()]
  log(`Classics: ${swept.filter(Boolean).length}/${SK.classic_themes.length} sweeps, ${merged.length} unique papers after dedupe`)
  const batches = []
  for (let i = 0; i < merged.length; i += 20) batches.push(merged.slice(i, i + 20))
  const verified = await parallel(batches.map((b, i) => () => agent(`${CONTEXT}\n\nYou are a FACT-CHECKER for a list of influential pre-2026 papers. For EVERY paper below: confirm it exists and was published (or first posted) in or before 2025; correct title, first author, year and venue; re-query the citation count from Semantic Scholar (preferred; https://api.semanticscholar.org/graph/v1/paper/search/match?query=...&fields=title,year,venue,citationCount — retry on 429) or OpenAlex; make the URL canonical and working (arXiv abs / DOI / official page); keep the Chinese fields but fix anything technically wrong or vague; keep only valid concept ids. Set status = verified / corrected / removed (removed if fabricated, published 2026+, or clearly not influential) with a short verify_note. Keep the 'theme' field as the first theme. Return every paper.\n\nPAPERS:\n${JSON.stringify(b.map(p => ({ ...p, theme: p.themes[0] })))}`,
    { label: `verify:classics${i}`, phase: 'Classics', schema: VERIFY_SCHEMA })))
  const out = []
  verified.forEach((v, i) => {
    if (!v) { batches[i].forEach(p => out.push({ ...p, theme: p.themes[0], status: 'unverified', verify_note: 'verification agent failed' })); return }
    v.papers.forEach(p => { const orig = byKey.get(norm(p.title).slice(0, 60)); out.push({ ...p, themes: orig ? orig.themes : [p.theme] }) })
  })
  log(`Classics verified: ${out.filter(p => p.status !== 'removed').length} kept, ${out.filter(p => p.status === 'removed').length} removed`)
  return out
})()

// ---------------- Branch D: guided walkthroughs ----------------
const ANCHORS = [
  { key: 'quark', name: 'Quark', url: 'https://arxiv.org/html/2411.16680v1', file: `${D}/anchor_quark.json`, steps: QUARK_STEPS },
  { key: 'ha', name: 'Ha et al. (Geometry-guided Online 3D Video Synthesis)', url: 'https://arxiv.org/html/2505.18932v1', file: `${D}/anchor_ha.json`, steps: HA_STEPS },
]
const guidedP = pipeline(
  ANCHORS,
  a => agent(`${CONTEXT}\n\nTASK: Write a GUIDED READING (精读导读) of ${a.name} that makes the paper easy to understand for the newcomer by tying every step to the foundation concepts. First read the FULL paper HTML (${a.url}, including appendix/supplement sections) and the deep-read file ${a.file}. Then produce:\n- story_zh: the paper as a story (problem -> key intuition -> solution -> what it buys and costs).\n- before_you_read: 6-12 prerequisite concept ids with why each is needed.\n- walkthrough: EXACTLY these steps, in this order, with these ids (titles may be polished):\n${a.steps}\n  Each step: what (inputs->outputs), a plain-language explanation that explicitly invokes the relevant foundation concepts, an analogy, the key equations from the paper rewritten in clean LaTeX with every symbol explained (and the paper's equation numbers in paper_ref), exact numbers/hyperparameters, why this design (and rejected alternatives), a common misunderstanding, concept_ids, and a check question with answer. Note paper typos or inconsistencies where they exist (e.g. missing sums, conflicting step counts) instead of silently fixing them.\n- tensor_trace: follow the data through the pipeline with concrete shapes.\n- reading_experiments: how to read each main table/figure/ablation and what it really shows (including weaknesses).\n- tradeoffs, faq (8-12 questions a newcomer would ask), exercises (4-6 hands-on mini projects that re-implement pieces in PyTorch/NumPy, from 入门 to 挑战, runnable on public data), glossary (15-30 terms).`,
    { label: `guide:${a.key}`, phase: 'Guided', schema: GUIDE_SCHEMA, effort: 'high' }),
  (draft, a) => agent(`${CONTEXT}\n\nYou are an ADVERSARIAL VERIFIER. Below is a guided reading of ${a.name}. Read the FULL paper HTML yourself (${a.url}, including appendices) and check EVERY claim, number, equation, tensor shape, design rationale and experiment interpretation against the paper. Assume errors exist and hunt for them: wrong hyperparameters, invented details, mis-stated equations, wrong shapes, overclaims, misattributed motivations, wrong section numbers. Also check that the explanations of foundation concepts are technically right and that concept_ids are the right ones. Fix everything in place, keep the step ids, and list each fix with the evidence (quote or section) in 'fixes'. If something cannot be verified from the paper, soften or remove it.\n\nDRAFT:\n${JSON.stringify(draft)}`,
    { label: `verify:${a.key}`, phase: 'Guided', schema: GUIDE_VERIFY_SCHEMA, effort: 'high' })
)

const [foundations, advanced, classics, guided] = await Promise.all([foundationsP, advancedP, classicsP, guidedP])
log(`Foundations ${foundations.filter(Boolean).length}/${SK.modules.length}, advanced groups ${advanced.filter(Boolean).length}/${ADV_GROUPS.length}, classics ${classics.length}, guides ${guided.filter(Boolean).length}/2`)

// ---------------- Final: roadmap + glossary ----------------
phase('Roadmap')
const mustRead = classics.filter(p => p.status !== 'removed' && p.must_read).map(p => `${p.title} (${p.year}) ${p.url}`)
const advSummary = advanced.filter(Boolean).flatMap(g => g.topics.map(t => `${t.id}: ${t.title_zh}`))
const exercises = guided.filter(Boolean).flatMap(g => g.exercises.map(e => `[${g.anchor}] ${e.title_zh} (${e.level})`))
const conceptResources = foundations.filter(Boolean).flatMap(m => m.concepts.map(c => `${c.id}: ${(c.resources || []).map(r => r.title + ' ' + r.url).join(' | ')}`))
const RM_SCHEMA = { type: 'object', properties: {
  overview_zh: S,
  stages: { type: 'array', items: { type: 'object', properties: {
    id: S, title_zh: S, duration_zh: S, goal_zh: S, concept_ids: SA, advanced_ids: SA,
    papers: { type: 'array', items: { type: 'object', properties: { title: S, url: S, why_zh: S }, required: ['title', 'url', 'why_zh'] } },
    resources: RES,
    project: { type: 'object', properties: { title_zh: S, task_zh: S, deliverable_zh: S, hints_zh: S }, required: ['title_zh', 'task_zh', 'deliverable_zh', 'hints_zh'] },
    checkpoint_zh: SA,
  }, required: ['id', 'title_zh', 'duration_zh', 'goal_zh', 'concept_ids', 'advanced_ids', 'papers', 'resources', 'project', 'checkpoint_zh'] } },
  tools: { type: 'array', items: { type: 'object', properties: { name: S, url: S, use_zh: S }, required: ['name', 'url', 'use_zh'] } },
  courses_books: RES,
  tips_zh: SA,
}, required: ['overview_zh', 'stages', 'tools', 'courses_books', 'tips_zh'] }
const GL_SCHEMA = { type: 'object', properties: { terms: { type: 'array', items: { type: 'object', properties: {
  term_en: S, term_zh: S, abbr: S, def_zh: S, concept_id: { type: 'string', description: 'a valid concept id or empty string' },
  category: { type: 'string', enum: ['几何与相机', '深度与重建', '渲染与图形', 'IBR 与表示', '学习与网络', '神经渲染', '视频与评测', '系统与显示'] },
}, required: ['term_en', 'term_zh', 'abbr', 'def_zh', 'concept_id', 'category'] } } }, required: ['terms'] }

const [roadmap, glossary] = await parallel([
  () => agent(`${CONTEXT}\n\nTASK: Design a LEARNING ROADMAP (学习路线) that takes the newcomer from zero to being able to read, reproduce and extend Quark and Ha et al., and then to reading 2025-2026 frontier work. 6-8 stages in order, each with duration (weeks, assuming ~15 h/week), goal, concept ids and advanced-topic ids covered, 3-6 papers to read (prefer the must-read classics below; real URLs), 2-4 resources (book chapters / course lectures / tutorials, real URLs), one hands-on project with a concrete deliverable (e.g. implement plane-sweep stereo, TSDF fusion + raycasting, a tiny NeRF, use gsplat, re-implement Ha et al.'s image-based TSDF on DyNeRF, an MPI renderer), and checkpoint questions. The last stages should culminate in reproducing parts of the anchors (the guided-reading exercises below) and moving to research. Also list the toolchain (COLMAP, Open3D, PyTorch3D, nerfstudio, gsplat, Kaolin, RAFT-Stereo, etc. with real URLs), core courses/books, and study tips.\n\nAdvanced topics: ${advSummary.join('; ')}\nMust-read classics: ${mustRead.join('\n')}\nGuided-reading exercises: ${exercises.join('; ')}\nConcept resources already cited: ${conceptResources.join('\n')}`,
    { label: 'roadmap', phase: 'Roadmap', schema: RM_SCHEMA, effort: 'high' }),
  () => agent(`${CONTEXT}\n\nTASK: Build a GLOSSARY (术语表) of 120-180 terms a newcomer meets when reading 3D telepresence / neural rendering papers, especially Quark and Ha et al. Each: English term, Chinese term, abbreviation (or empty), a precise 1-2 sentence Chinese definition, the best matching concept id (or empty), and a category. Cover geometry, depth, rendering, IBR/representations, networks, neural rendering, video/metrics, systems/displays. Include all terms below (dedupe) and add missing important ones.\n\nConcepts: ${ALL_CONCEPTS.map(c => c.id + ' ' + c.name_zh).join('; ')}\nGuided-reading glossaries: ${JSON.stringify(guided.filter(Boolean).flatMap(g => g.glossary.map(t => t.term_en + ' / ' + t.term_zh)))}\nAdvanced key ideas: ${JSON.stringify(advanced.filter(Boolean).flatMap(g => g.topics.flatMap(t => t.key_ideas.map(k => k.name_zh))))}`,
    { label: 'glossary', phase: 'Roadmap', schema: GL_SCHEMA }),
])

return { foundations, advanced, classics, guided, roadmap, glossary }
