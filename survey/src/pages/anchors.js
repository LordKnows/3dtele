  // ================= page: 锚点论文（研究视角） =================
  var anchors = DATA.anchors || {};
  function withId(node, id) { node.id = id; return node; }
  function anchorView(a) {
    if (!a) return el("p", { class: "note", text: "该部分数据缺失。" });
    var c = a.citation || {};
    return el("div", { class: "anchor-body" }, [
      el("div", { class: "meta-line" }, [
        el("span", { text: c.authors || "" }), el("span", { text: c.affiliations || "" }), el("span", { class: "mono", text: (c.venue || "") + (c.year ? " · " + c.year : "") }),
        link("论文", c.url), safeUrl(c.project_page) ? link("项目主页", c.project_page) : null, c.code_status ? el("span", { text: "代码：" + c.code_status }) : null
      ]),
      el("p", { class: "tldr", text: a.tldr_zh || "" }),
      a.problem_setting_zh ? el("div", { class: "prose" }, [el("h3", { class: "sub", text: "问题设定" })].concat(paras(a.problem_setting_zh))) : null,
      el("div", { class: "blk" }, [el("h3", { class: "sub", text: "流水线" }), el("ol", { class: "stages" }, arr(a.pipeline_zh).map(function (s) { return el("li", null, [el("div", null, [el("b", { text: s.stage }), el("span", { text: s.detail })])]); }))]),
      arr(a.system_perf).length ? el("div", { class: "blk" }, [el("h3", { class: "sub", text: "系统与性能" }), el("div", { class: "kv" }, arr(a.system_perf).map(function (x) { return el("div", null, [el("span", { class: "k", text: x.item }), el("span", { class: "v", text: x.value })]); }))]) : null,
      arr(a.key_design_choices_zh).length ? el("div", { class: "blk" }, [el("h3", { class: "sub", text: "关键设计选择" }), el("div", { class: "tbl-wrap" }, [el("table", null, [
        el("thead", null, [el("tr", null, [el("th", { text: "选择" }), el("th", { text: "理由" }), el("th", { text: "被放弃的替代方案" })])]),
        el("tbody", null, arr(a.key_design_choices_zh).map(function (d) { return el("tr", null, [el("td", { class: "dim", style: "white-space:normal;min-width:160px", text: d.choice }), el("td", { text: d.rationale }), el("td", { text: d.alternatives_rejected })]); }))
      ])])]) : null,
      a.training_zh ? el("div", { class: "prose" }, [el("h3", { class: "sub", text: "训练" })].concat(paras(a.training_zh))) : null,
      arr(a.results_zh).length ? el("div", { class: "blk" }, [el("h3", { class: "sub", text: "实验结果" }), ul(a.results_zh, function (r) { return el("span", null, [el("b", { text: r.dataset + "：" }), r.finding]); })]) : null,
      arr(a.ablations_zh).length ? el("div", { class: "blk" }, [el("h3", { class: "sub", text: "消融" }), ul(a.ablations_zh)]) : null,
      el("div", { class: "two" }, [
        el("div", { class: "blk" }, [el("h3", { class: "sub", text: "作者承认的局限" }), ul(a.limitations_stated_zh)]),
        el("div", { class: "blk" }, [el("h3", { class: "sub", text: "精读发现的未言明问题" }), ul(a.limitations_unstated_zh)])
      ]),
      el("div", { class: "two" }, [
        el("div", { class: "blk" }, [el("h3", { class: "sub", text: "前序工作" }), ul(arr((a.lineage || {}).predecessors), function (p) { return el("span", null, [link(p.title, p.url), " (" + p.year + ") — " + (p.note_zh || "")]); })]),
        el("div", { class: "blk" }, [el("h3", { class: "sub", text: "后续 / 竞争工作" }), ul(arr((a.lineage || {}).successors), function (p) { return el("span", null, [link(p.title, p.url), " (" + p.year + ") — " + (p.note_zh || "")]); })])
      ]),
      arr(a.takeaways_for_telepresence_zh).length ? el("div", { class: "blk" }, [el("h3", { class: "sub", text: "对 3D 临场的启示" }), ul(a.takeaways_for_telepresence_zh)]) : null
    ]);
  }
  function compareView(c) {
    if (!c) return el("p", { class: "note", text: "该部分数据缺失。" });
    return el("div", { class: "anchor-body" }, [
      el("div", { class: "tbl-wrap" }, [el("table", null, [
        el("thead", null, [el("tr", null, [el("th", { text: "维度" }), el("th", { text: "Quark" }), el("th", { text: "Ha et al." })])]),
        el("tbody", null, arr(c.comparison_table).map(function (r) { return el("tr", null, [el("td", { class: "dim", text: r.dimension }), el("td", { text: r.quark }), el("td", { text: r.ha })]); }))
      ])]),
      el("div", { class: "prose" }, [el("h3", { class: "sub", text: "两种设计哲学" })].concat(paras(c.philosophy_zh))),
      el("div", { class: "prose" }, [el("h3", { class: "sub", text: "互补性" })].concat(paras(c.complementarity_zh))),
      el("div", { class: "prose" }, [el("h3", { class: "sub", text: "取两者之长的临场系统草图" })].concat(paras(c.combined_system_sketch_zh))),
      el("div", { class: "blk" }, [el("h3", { class: "sub", text: "共同盲区" }), ul(c.shared_blindspots_zh)])
    ]);
  }
  addSection("anchors", "锚点论文", [
    secHead("Anchor papers", "两篇锚点论文精读（研究视角）", "偏研究者视角的精读：精确数字、设计选择、局限与谱系。想从零读懂，请先看入门学习部分的“精读导读”页。"),
    el("p", { class: "note" }, [(function () { var a = el("a", { text: "前往精读导读 →" }); a.setAttribute("href", "guided.html"); return a; })()]),
    el("div", { class: "panel" }, [makeTabs([
      { id: "quark", label: "Quark", node: function () { return withId(anchorView(anchors.quark), "anchor-quark"); } },
      { id: "ha", label: "Ha et al.", node: function () { return withId(anchorView(anchors.ha), "anchor-ha"); } },
      { id: "cmp", label: "对比与互补", node: function () { return withId(compareView(anchors.compare), "anchor-cmp"); } }
    ], "atlas.anchorTab")])
  ]);
  addTocItem("anchor-quark", "Quark");
  addTocItem("anchor-ha", "Ha et al.");
  addTocItem("anchor-cmp", "对比与互补");
