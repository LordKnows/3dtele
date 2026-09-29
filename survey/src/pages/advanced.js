  // ================= page: 进阶专题 =================
  var advanced = arr(DATA.advanced);
  // ---------- Advanced ----------
  if (advanced.length) {
    var prio = { must: "必读", should: "建议", optional: "选读" };
    addSection("advanced", "进阶专题", [
      secHead("Advanced topics", "进阶专题与奠基论文", meta.advanced_lede || ""),
      el("div", { style: "display:grid;gap:10px" }, advanced.map(function (t) {
        return el("details", { class: "card-d", id: "adv-" + t.id }, [
          el("summary", null, [el("h3", { style: "font-size:17px", text: t.title_zh }), el("span", { class: "cnt", text: t.title_en + " · " + arr(t.papers).length + " 篇奠基论文" }), el("span", { class: "tog" })]),
          el("div", { class: "area-body" }, [
            chipRow("前置概念", arr(t.prereqs).map(function (c) { return cChip(c); })),
            el("div", { class: "prose" }, paras(t.overview_zh)),
            arr(t.key_ideas).length ? blk("核心思想", [el("div", { class: "subgrid" }, arr(t.key_ideas).map(function (k) { return el("div", { class: "subcard" }, [el("b", { text: k.name_zh }), el("p", { text: k.explain_zh })]); }))]) : null,
            arr(t.equations).length ? blk("关键公式", [eqList(t.equations)]) : null,
            arr(t.evolution).length ? blk("演进", [el("div", { class: "timeline" }, arr(t.evolution).slice().sort(function (a, b) { return (a.year || 0) - (b.year || 0); }).map(function (e) { return el("div", null, [el("span", { class: "y", text: String(e.year) }), el("span", { text: e.milestone_zh })]); }))]) : null,
            arr(t.papers).length ? blk("奠基论文", [el("div", { class: "tbl-wrap" }, [el("table", null, [
              el("thead", null, [el("tr", null, ["优先级", "论文", "引用", "贡献"].map(function (h) { return el("th", { text: h }); }))]),
              el("tbody", null, arr(t.papers).map(function (p) { return el("tr", null, [el("td", null, [el("span", { class: "pill " + (p.priority || "optional"), text: prio[p.priority] || "选读" })]), el("td", { style: "min-width:240px" }, [link(p.title, p.url), el("small", { style: "display:block;color:var(--muted);font-size:12px", text: [p.authors, p.venue, p.year].filter(Boolean).join(" · ") })]), el("td", { class: "code", text: fmtCit(p.citations) }), el("td", { style: "min-width:260px;color:var(--ink-2)", text: p.role_zh })]); }))
            ])])]) : null,
            textBlk("与两篇锚点论文的关系", t.relation_to_anchors_zh),
            el("div", { class: "two" }, [arr(t.debates_zh).length ? blk("争论与分歧", [ul(t.debates_zh)]) : null, arr(t.open_questions_zh).length ? blk("开放问题", [ul(t.open_questions_zh)]) : null]),
            arr(t.resources).length ? blk("学习资源", [resList(t.resources)]) : null
          ])
        ]);
      }))
    ]);
  }
  advanced.forEach(function (t) { addTocItem("adv-" + t.id, t.title_zh); });
