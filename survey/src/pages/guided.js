  // ================= page: 精读导读 =================
  var guides = DATA.guided || {};
  // ---------- Guided reading ----------
  function diagramQuark() {
    return {
      w: 960, h: 300,
      nodes: [
        { x: 10, y: 118, w: 132, h: 64, t: "输入视角 × M", s: "RGB + 相机，M = 8", k: "q1" },
        { x: 162, y: 118, w: 140, h: 64, t: "编码", s: "特征金字塔 + 射线编码 γ", k: "q2" },
        { x: 322, y: 118, w: 132, h: 64, t: "初始化 LDM", s: "24 层 × 36×64", k: "q4" },
        { x: 322, y: 212, w: 132, h: 58, t: "LDM 参数化", s: "等视差锚点 + 视差带", k: "q3", data: true },
        { x: 496, y: 64, w: 118, h: 58, t: "Render", s: "LDM → 输入视角 Ĩ", k: "q5" },
        { x: 640, y: 64, w: 118, h: 58, t: "Update", s: "对比 Ĩ 与观测 → Δ", k: "q6" },
        { x: 568, y: 160, w: 118, h: 58, t: "Fuse", s: "One-to-many attention", k: "q7" },
        { x: 800, y: 64, w: 150, h: 64, t: "上采样后激活", s: "3.75× 到 1080p", k: "q9" },
        { x: 800, y: 170, w: 150, h: 64, t: "IBR 混合 + over", s: "全分辨率像素凸组合", k: "q10" }
      ],
      loop: { x: 480, y: 26, w: 294, h: 250, label: "Update & Fuse × 5（由粗到细）", noteK: "q8", note: "每步分辨率 ×2，Layer Collapse 层数 ÷2" },
      edges: [
        { d: "M142,150 L162,150" }, { d: "M302,150 L322,150" },
        { d: "M388,212 L388,182" },
        { d: "M454,150 C470,150 470,93 496,93" },
        { d: "M614,93 L640,93" },
        { d: "M699,122 C699,150 686,189 686,189" },
        { d: "M568,189 C520,189 530,122 540,122", fb: true },
        { d: "M774,96 L800,96" },
        { d: "M875,128 L875,170" },
        { d: "M875,234 L875,268" }
      ],
      out: { x: 875, y: 285, text: "新视角图像（1080p，≈30 ms/帧）" }
    };
  }
  function diagramHa() {
    return {
      w: 960, h: 330,
      nodes: [
        { x: 10, y: 128, w: 136, h: 64, t: "K 个 RGB-D 视角", s: "t 时刻，K = 4", k: "h1" },
        { x: 10, y: 236, w: 136, h: 58, t: "深度来源", s: "RAFT-Stereo / 传感器", k: "h2", data: true },
        { x: 176, y: 26, w: 164, h: 64, t: "逐视角前向 splat", s: "像素大小的不透明高斯", k: "h3" },
        { x: 372, y: 26, w: 150, h: 64, t: "Iₖ, αₖ, Dₖ", s: "K 份目标视角图像", k: "h3", data: true },
        { x: 176, y: 128, w: 110, h: 64, t: "差分掩码 M", s: "哪里在动", k: "h4" },
        { x: 304, y: 128, w: 110, h: 64, t: "深度 EMA", s: "只滤静止区域", k: "h5" },
        { x: 432, y: 128, w: 140, h: 64, t: "图像空间 TSDF", s: "sₖ 截断 τ，加权", k: "h6" },
        { x: 590, y: 128, w: 128, h: 64, t: "光线步进", s: "零交叉 → 深度 𝒟ᵗ", k: "h8" },
        { x: 432, y: 240, w: 140, h: 58, t: "上一帧深度 𝒟ᵗ⁻¹", s: "时间反馈 ω_tmp", k: "h9" },
        { x: 752, y: 60, w: 160, h: 72, t: "几何引导混合 U-Net", s: "9K+1 通道输入", k: "h10" },
        { x: 752, y: 190, w: 160, h: 64, t: "wₖ、w_BG、I_BG", s: "混合出最终图像", k: "h11" }
      ],
      edges: [
        { d: "M78,236 L78,192" },
        { d: "M146,146 C160,146 160,58 176,58" },
        { d: "M146,160 L176,160" },
        { d: "M340,58 L372,58" },
        { d: "M286,160 L304,160" }, { d: "M414,160 L432,160" }, { d: "M572,160 L590,160" },
        { d: "M502,240 L502,192" },
        { d: "M654,192 C654,270 600,269 572,269", fb: true },
        { d: "M522,58 C640,58 700,84 752,84" },
        { d: "M718,160 C735,160 735,112 752,112" },
        { d: "M832,132 L832,190" },
        { d: "M832,254 L832,292" }
      ],
      out: { x: 832, y: 312, text: "输出图像 ℐᵗ（≈40–100 ms/帧，不含立体深度）" },
      notes: [{ x: 600, y: 300, text: "虚线：下一帧回灌" }]
    };
  }
  function drawDiagram(spec, anchorKey, title) {
    var svg = sv("svg", { class: "diagram", viewBox: "0 0 " + spec.w + " " + spec.h, role: "img", "aria-label": title });
    var defs = sv("defs", null, [
      sv("marker", { id: "ah-" + anchorKey, viewBox: "0 0 10 10", refX: "9", refY: "5", markerWidth: "7", markerHeight: "7", orient: "auto-start-reverse" }, [sv("path", { d: "M0,0 L10,5 L0,10 z", class: "dhead" })]),
      sv("marker", { id: "ahf-" + anchorKey, viewBox: "0 0 10 10", refX: "9", refY: "5", markerWidth: "7", markerHeight: "7", orient: "auto-start-reverse" }, [sv("path", { d: "M0,0 L10,5 L0,10 z", class: "dhead fb" })])
    ]);
    svg.appendChild(defs);
    if (spec.loop) {
      var lp = spec.loop;
      svg.appendChild(sv("rect", { class: "dloop", x: lp.x, y: lp.y, width: lp.w, height: lp.h, rx: 12 }));
      svg.appendChild(sv("text", { class: "dlabel", x: lp.x + 14, y: lp.y + 22, text: lp.label }));
      var ng = sv("g", { class: "dnode click", tabindex: "0", role: "button", "aria-label": "跳到导读 " + lp.noteK });
      ng.appendChild(sv("text", { class: "dnote", x: lp.x + 14, y: lp.y + lp.h - 14, text: "▸ " + lp.note + "（" + lp.noteK + "）" }));
      ng.addEventListener("click", function () { goTo(walkId(anchorKey, lp.noteK)); });
      ng.addEventListener("keydown", function (e) { if (e.key === "Enter" || e.key === " ") { e.preventDefault(); goTo(walkId(anchorKey, lp.noteK)); } });
      svg.appendChild(ng);
    }
    spec.edges.forEach(function (e) { svg.appendChild(sv("path", { class: "dedge" + (e.fb ? " fb" : ""), d: e.d, "marker-end": "url(#" + (e.fb ? "ahf-" : "ah-") + anchorKey + ")" })); });
    spec.nodes.forEach(function (n) {
      var g = sv("g", { class: "dnode click" + (n.data ? " data" : ""), tabindex: "0", role: "button", "aria-label": n.t + "，跳到导读 " + n.k });
      g.appendChild(sv("rect", { x: n.x, y: n.y, width: n.w, height: n.h, rx: 8 }));
      g.appendChild(sv("text", { class: "k", x: n.x + 10, y: n.y + 16, text: n.k }));
      g.appendChild(sv("text", { class: "t", x: n.x + 10, y: n.y + 35, text: n.t }));
      g.appendChild(sv("text", { class: "s", x: n.x + 10, y: n.y + 52, text: n.s }));
      var go = function () { goTo(walkId(anchorKey, n.k)); };
      g.addEventListener("click", go);
      g.addEventListener("keydown", function (e) { if (e.key === "Enter" || e.key === " ") { e.preventDefault(); go(); } });
      svg.appendChild(g);
    });
    if (spec.out) svg.appendChild(sv("text", { class: "dnote", x: spec.out.x, y: spec.out.y, "text-anchor": "middle", text: spec.out.text }));
    arr(spec.notes).forEach(function (n) { svg.appendChild(sv("text", { class: "dnote", x: n.x, y: n.y, text: n.text })); });
    return el("div", { class: "diagram-wrap" }, [svg]);
  }
  function stepCard(anchorKey, s) {
    return el("details", { class: "step", id: walkId(anchorKey, s.id) }, [
      el("summary", null, [el("span", { class: "sid", text: s.id }), el("div", { class: "st" }, [el("b", { text: s.title_zh }), s.paper_ref ? el("small", { text: s.paper_ref }) : null]), el("span", { class: "tog" })]),
      el("div", { class: "step-body" }, [
        chipRow("需要的基础", arr(s.concept_ids).map(function (c) { return cChip(c); })),
        chipRow("延伸专题", arr(s.adv_ids).map(aChip)),
        asideBox("这一步做什么", s.what_zh),
        textBlk("白话解释", s.plain_zh),
        asideBox("类比", s.analogy_zh),
        arr(s.equations).length ? blk("公式逐项拆解", [eqList(s.equations)]) : null,
        el("div", { class: "idea-grid" }, [textBlk("具体数字", s.numbers_zh), textBlk("为什么这样设计", s.why_design_zh)]),
        textBlk("容易误解的地方", s.pitfalls_zh),
        s.check_q_zh ? blk("自测", [qaList([{ q: s.check_q_zh, a: s.check_a_zh }], "q", "a")]) : null
      ])
    ]);
  }
  function guideView(anchorKey) {
    var g = guides[anchorKey];
    if (!g) return el("p", { class: "note", text: "该部分数据缺失。" });
    var spec = anchorKey === "quark" ? diagramQuark() : diagramHa();
    return el("div", { class: "anchor-body", id: "guide-" + anchorKey }, [
      el("div", { class: "prose" }, paras(g.story_zh)),
      blk("流程图（点击方框跳到对应步骤）", [drawDiagram(spec, anchorKey, (anchorKey === "quark" ? "Quark" : "Ha et al.") + " 流程图")]),
      arr(g.before_you_read).length ? blk("读之前先掌握", [el("div", { class: "checklist" }, arr(g.before_you_read).map(function (b) { return el("div", null, [cChip(b.concept_id) || el("b", { text: b.concept_id }), el("span", { text: b.why_zh })]); }))]) : null,
      blk("逐步拆解", [el("div", { style: "display:grid;gap:8px" }, arr(g.walkthrough).map(function (s) { return stepCard(anchorKey, s); }))]),
      arr(g.tensor_trace).length ? blk("张量形状追踪", [el("div", { class: "tbl-wrap" }, [el("table", null, [
        el("thead", null, [el("tr", null, ["阶段", "张量", "形状", "说明"].map(function (h) { return el("th", { text: h }); }))]),
        el("tbody", null, arr(g.tensor_trace).map(function (r) { return el("tr", null, [el("td", { text: r.stage_zh }), el("td", { class: "code", text: r.tensor }), el("td", { class: "code", text: r.shape }), el("td", { text: r.note_zh })]); }))
      ])])]) : null,
      arr(g.reading_experiments).length ? blk("怎么读实验部分", [el("div", { class: "cards" }, arr(g.reading_experiments).map(function (r) { return el("div", { class: "card" }, [el("h4", { text: r.item }), el("p", { text: r.how_to_read_zh }), el("span", { class: "lbl", text: "真正说明了什么" }), el("p", { text: r.takeaway_zh })]); }))]) : null,
      arr(g.tradeoffs).length ? blk("设计取舍", [el("div", { class: "tbl-wrap" }, [el("table", null, [
        el("thead", null, [el("tr", null, ["选择", "换来的", "付出的"].map(function (h) { return el("th", { text: h }); }))]),
        el("tbody", null, arr(g.tradeoffs).map(function (r) { return el("tr", null, [el("td", { class: "dim", style: "white-space:normal", text: r.choice_zh }), el("td", { text: r.gain_zh }), el("td", { text: r.cost_zh })]); }))
      ])])]) : null,
      arr(g.faq).length ? blk("新手常问", [qaList(g.faq, "q_zh", "a_zh")]) : null,
      arr(g.exercises).length ? blk("动手练习", [el("div", { class: "cards" }, arr(g.exercises).map(function (x) { return el("div", { class: "card" }, [el("div", { class: "chips" }, [el("span", { class: "pill " + (x.level === "入门" ? "should" : x.level === "进阶" ? "must" : "drop"), text: x.level })]), el("h4", { text: x.title_zh }), el("p", { text: x.task_zh }), x.expected_zh ? el("p", { class: "note", text: "预期结果：" + x.expected_zh }) : null, x.hint_zh ? el("p", { class: "note", text: "提示：" + x.hint_zh }) : null, chipRow("概念", arr(x.concept_ids).map(function (c) { return cChip(c, true); }))]); }))]) : null
    ]);
  }
  if (guides.quark || guides.ha) {
    addSection("guided", "精读导读", [
      secHead("Guided reading", "精读导读：用基础知识读懂两篇锚点论文", meta.guided_lede || ""),
      el("div", { class: "panel" }, [makeTabs([
        { id: "quark", label: "Quark 导读", node: function () { return guideView("quark"); } },
        { id: "ha", label: "Ha et al. 导读", node: function () { return guideView("ha"); } }
      ], "atlas.guideTab")])
    ]);
    if (guides.quark) addTocItem("guide-quark", "Quark 导读");
    if (guides.ha) addTocItem("guide-ha", "Ha et al. 导读");
  }
