  // ================= article: one Foundations concept =================
  (function () {
    var c = DATA.concept || {};
    if (!c.id) return;
    art.id = "concept-" + c.id;
    var mod = XREF[DATA.module] || {};

    var prereqs = arr(c.prereqs).map(function (p) { return xlink("concept-" + p, XREF["concept-" + p] ? XREF["concept-" + p].t : p); }).filter(Boolean);
    var metaLine = [];
    if (prereqs.length) metaLine.push(marginnote([noteLabel("阅读前需要")].concat(joinNodes(prereqs, "；"))));
    metaLine.push(xlink(DATA.module, mod.t), " · 约 " + (DATA.readMin || 1) + " 分钟");
    articleHead({ title: c.name_zh, subtitle: c.name_en, meta: metaLine, epigraph: c.tldr_zh });

    function joinNodes(nodes, sep) {
      var out = [];
      nodes.forEach(function (n, i) { if (i) out.push(sep); out.push(n); });
      return out;
    }

    // 直觉: the analogy sits in the margin beside the first paragraph.
    var intuition = paras(c.intuition_zh);
    if (str(c.analogy_zh).trim() && intuition.length) intuition[0].insertBefore(marginnote([noteLabel("类比")].concat(rich(c.analogy_zh))), intuition[0].firstChild);
    if (intuition.length) section("intuition", "直觉", intuition);

    var eqs = eqList(c.equations);
    if (eqs) section("equations", "公式", [eqs]);
    if (str(c.worked_example_zh).trim()) section("example", "例子", lines(c.worked_example_zh));
    if (arr(c.pitfalls_zh).length) section("pitfalls", "易错点", [el("ol", null, arr(c.pitfalls_zh).map(function (t) { return el("li", null, rich(t)); }))]);
    if (str(c.in_field_zh).trim()) section("in-field", "在 3D 临场系统中", paras(c.in_field_zh));

    // 案例: where each key paper uses the concept; the paper location is a side note, guide steps a margin note.
    var steps = arr(DATA.walk);
    var cases = [];
    [["quark", c.in_quark], ["ha", c.in_ha]].forEach(function (pair) {
      var anchor = pair[0], u = pair[1] || {};
      var head = el("h3", null, [anchorName(anchor),
        str(u.where).trim() ? sidenote([noteLabel("论文位置")].concat(rich(u.where))) : null,
        el("span", { class: "used", text: u.used ? "用到" : "未用" })]);
      cases.push(head);
      var body = paras(u.how_zh);
      var mine = steps.filter(function (k) { return k.indexOf("walk-" + anchor + "-") === 0 && hasX(k); });
      if (mine.length && body.length) {
        var links = [];
        mine.forEach(function (k, i) { if (i) links.push(el("br")); links.push(xlink(k, XREF[k].n + " " + XREF[k].t)); });
        body[0].insertBefore(marginnote([noteLabel("导读步骤")].concat(links)), body[0].firstChild);
      }
      cases = cases.concat(body);
    });
    section("cases", "案例：Quark 与 Ha 如何使用", cases);
    function anchorName(a) { return a === "quark" ? "Quark" : "Ha et al."; }

    // The other deep reads: their walkthrough steps that build on this concept, labelled with the paper.
    var more = steps.filter(function (k) { return !/^walk-(quark|ha)-/.test(k) && hasX(k); });
    if (more.length) {
      var byPaper = [], seen = {};
      more.forEach(function (k) {
        var paper = str(XREF[k].m).split(" · ")[1] || "";
        if (!seen[paper]) { seen[paper] = []; byPaper.push(paper); }
        seen[paper].push(k);
      });
      section("cases-more", "更多精读中的用法", [el("ul", { class: "refs wide-kind" }, byPaper.map(function (paper) {
        var links = [];
        seen[paper].forEach(function (k, i) { if (i) links.push(el("br")); links.push(xlink(k, XREF[k].n + " " + XREF[k].t)); });
        return el("li", null, [el("span", { class: "kind", text: paper }), el("div", null, links)]);
      }))]);
    }

    if (arr(c.self_check).length) {
      section("self-check", "自测", [el("ol", { class: "quiz" }, arr(c.self_check).map(function (q) {
        return el("li", null, [el("p", null, rich(q.q_zh)), el("details", null, [el("summary", { text: "答案" }), el("p", null, rich(q.a_zh))])]);
      }))]);
    }

    // 延伸阅读: resources with their notes, then topics and classic papers that build on this concept.
    var further = [];
    var ty = { book: "教材", course: "课程", paper: "论文", tutorial: "教程", code: "代码", video: "视频", blog: "文章" };
    if (arr(c.resources).length) {
      further.push(el("h3", { text: "学习资源" }));
      further.push(el("ul", { class: "refs" }, arr(c.resources).map(function (r) {
        return el("li", null, [el("span", { class: "kind", text: ty[r.type] || r.type || "" }),
          el("div", null, [link(r.title, r.url), str(r.note_zh).trim() ? el("div", { class: "gloss" }, rich(r.note_zh)) : null])]);
      })));
    }
    var adv = arr(DATA.adv).filter(hasX);
    if (adv.length) {
      further.push(el("h3", { text: "进阶专题" }));
      further.push(el("ul", { class: "refs" }, adv.map(function (k) {
        return el("li", null, [el("span", { class: "kind", text: "专题" }), el("div", null, [xlink(k, XREF[k].t), XREF[k].e ? el("div", { class: "en", text: XREF[k].e }) : null])]);
      })));
    }
    var cls = arr(DATA.classics).filter(hasX);
    if (cls.length) {
      further.push(el("h3", { text: "经典论文" }));
      further.push(el("ul", { class: "refs papers" }, cls.map(function (k) {
        return el("li", null, [el("span", { class: "yr", text: str(XREF[k].m).replace(/^Classics · /, "") }), xlink(k, XREF[k].t)]);
      })));
    }
    if (further.length) section("further", "延伸阅读", further);

    seriesNav(DATA.prev, DATA.next, "basics/foundations/index.html", "Foundations 目录");
  })();
