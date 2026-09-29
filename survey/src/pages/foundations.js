  // ================= page: 基础知识 =================
  (function () {
    var modules = arr(DATA.modules);
    if (!modules.length) return;
    var rev = DATA.rev || {};
    var walkBy = rev.walkBy || {}, classicBy = rev.classicBy || {}, advBy = rev.advBy || {};
    function usePill(u, label) { var on = u && u.used; return el("span", { class: "pill " + (on ? "yes" : "no"), text: label + (on ? " 用到" : " 未用") }); }
    function useBox(u, anchorKey, cid) {
      u = u || {};
      var steps = arr(walkBy[cid]).filter(function (w) { return w.anchor === anchorKey; });
      return el("div", null, [
        el("h5", null, [anchorShort[anchorKey], usePill(u, "")]),
        u.where ? el("small", { text: u.where }) : null,
        el("p", { text: u.how_zh || "" }),
        steps.length ? chipRow("导读", steps.map(function (w) { return refChip(walkId(w.anchor, w.id), w.id + " " + w.title, true); })) : null
      ]);
    }
    function conceptCard(c) {
      var cls = arr(classicBy[c.id]);
      return el("details", { class: "concept", id: "concept-" + c.id }, [
        el("summary", null, [
          el("div", { class: "nm" }, [el("b", { text: c.name_zh }), el("span", { text: c.name_en })]),
          el("div", { class: "uses" }, [usePill(c.in_quark, "Quark"), usePill(c.in_ha, "Ha")]),
          el("p", { class: "tl", text: c.tldr_zh })
        ]),
        el("div", { class: "concept-body" }, [
          chipRow("前置", arr(c.prereqs).map(function (p) { return cChip(p, true); })),
          textBlk("直觉", c.intuition_zh),
          asideBox("类比", c.analogy_zh),
          arr(c.equations).length ? blk("关键公式", [eqList(c.equations)]) : null,
          textBlk("例子", c.worked_example_zh),
          arr(c.pitfalls_zh).length ? blk("易错点", [ul(c.pitfalls_zh)]) : null,
          blk("在两篇锚点论文中", [el("div", { class: "anchor-use" }, [useBox(c.in_quark, "quark", c.id), useBox(c.in_ha, "ha", c.id)])]),
          textBlk("在 3D 临场系统中", c.in_field_zh),
          chipRow("延伸到进阶专题", arr(advBy[c.id]).map(aChip)),
          cls.length ? chipRow("相关经典论文", cls.slice(0, 8).map(function (x) { return refChip("classic-" + x.i, x.title.length > 42 ? x.title.slice(0, 40) + "…" : x.title, true); })) : null,
          arr(c.resources).length ? blk("学习资源", [resList(c.resources)]) : null,
          arr(c.self_check).length ? blk("自测", [qaList(c.self_check, "q_zh", "a_zh")]) : null
        ])
      ]);
    }
    var overview = el("div", { class: "mods" }, modules.map(function (m) {
      return el("button", { type: "button", class: "mod", onclick: function () { goTo("module-" + m.id); } }, [el("i", { text: m.id + " · " + arr(m.concepts).length + " 个概念" }), el("b", { text: m.title_zh }), el("span", { text: m.goal_zh })]);
    }));
    var mods = modules.map(function (m, i) {
      var d = el("details", { class: "area", id: "module-" + m.id }, [
        el("summary", null, [el("h3", { text: m.id + " · " + m.title_zh }), el("span", { class: "cnt", text: m.title_en + " · " + arr(m.concepts).length + " 个概念" }), el("span", { class: "tog" })]),
        el("div", { class: "area-body" }, [
          el("div", { class: "prose" }, paras(m.intro_zh)),
          asideBox("怎么学", m.study_tips_zh),
          el("div", { style: "display:grid;gap:8px" }, arr(m.concepts).map(conceptCard))
        ])
      ]);
      if (i === 0) d.open = true;
      return d;
    });
    addSection("foundations", "基础知识", [
      secHead("Foundations", "基础知识：读懂这个领域需要的 " + Object.keys(conceptName).length + " 个概念", meta.foundations_lede || ""),
      overview
    ].concat(mods));
    modules.forEach(function (m) { addTocItem("module-" + m.id, m.id + " · " + m.title_zh); });
  })();
