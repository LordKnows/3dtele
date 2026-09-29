  // ================= page: 学习路线 =================
  (function () {
    var roadmap = DATA.roadmap || {};
    var stages = arr(roadmap.stages);
    if (!stages.length) return;
    var nodes = stages.map(function (s, i) {
      var pr = s.project || {};
      return el("details", { class: "stage", id: "stage-" + i }, [
        el("summary", null, [
          el("span", { class: "num", text: String(i + 1) }),
          el("div", { class: "head" }, [el("h3", { text: s.title_zh }), el("p", { text: s.goal_zh })]),
          el("span", { class: "dur", text: s.duration_zh || "" })
        ]),
        el("div", { class: "area-body" }, [
          chipRow("概念", arr(s.concept_ids).map(function (c) { return cChip(c); })),
          chipRow("进阶专题", arr(s.advanced_ids).map(aChip)),
          arr(s.papers).length ? blk("要读的论文", [ul(s.papers, function (p) { return el("span", null, [link(p.title, p.url), p.why_zh ? " — " + p.why_zh : ""]); })]) : null,
          arr(s.resources).length ? blk("课程与资料", [resList(s.resources)]) : null,
          blk("动手项目：" + (pr.title_zh || ""), [el("div", { class: "prose" }, paras(pr.task_zh)), pr.deliverable_zh ? el("p", { class: "note", text: "交付物：" + pr.deliverable_zh }) : null, pr.hints_zh ? el("p", { class: "note", text: "提示：" + pr.hints_zh }) : null]),
          arr(s.checkpoint_zh).length ? blk("学完应能回答", [ul(s.checkpoint_zh)]) : null
        ])
      ]);
    });
    addSection("roadmap", "学习路线", [
      secHead("Roadmap", "学习路线：从零到能复现两篇锚点论文"),
      el("div", { class: "prose" }, paras(roadmap.overview_zh)),
      el("div", { class: "roadmap" }, nodes),
      el("div", { class: "two", id: "roadmap-resources" }, [
        arr(roadmap.courses_books).length ? blk("核心课程与教材", [resList(roadmap.courses_books)]) : null,
        arr(roadmap.tools).length ? blk("工具链", [ul(roadmap.tools, function (t) { return el("span", null, [link(t.name, t.url), " — " + str(t.use_zh)]); })]) : null
      ]),
      arr(roadmap.tips_zh).length ? blk("学习建议", [ul(roadmap.tips_zh)]) : null
    ]);
    stages.forEach(function (s, i) {
      var t = str(s.title_zh), head = t.split("：")[0], rest = t.indexOf("：") >= 0 ? t.slice(t.indexOf("：") + 1).split("——")[0] : "";
      addTocItem("stage-" + i, rest ? head + " · " + rest : head);
    });
    addTocItem("roadmap-resources", "课程、教材与工具链");
  })();
