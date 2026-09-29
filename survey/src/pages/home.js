  // ================= page: 概览（首页） =================
  var H = DATA.home || {};
  var counts = H.counts || {};
  function pageAnchor(file, cls, kids) { var a = el("a", { class: cls }, kids); a.setAttribute("href", file); return a; }

  addSection("top", "概览", [
    el("div", { class: "hero" }, [
      el("div", { class: "eyebrow", text: "Field survey & study guide · " + (meta.date || "") + " · 3D telepresence / real-time 3D vision" }),
      el("h1", { text: "3D 临场研究图谱" }),
      el("p", { class: "sub", text: meta.subtitle || "" }),
      el("div", { class: "anchors-line" }, [
        el("span", { class: "chip accent", text: "锚点 A · Quark (SIGGRAPH Asia 2024)" }),
        el("span", { class: "chip accent", text: "锚点 B · Ha et al. (CVPR 2025)" })
      ]),
      el("div", { class: "ramp", "aria-hidden": "true" }),
      el("div", { class: "stats" }, [
        el("div", { class: "stat" }, [el("b", { text: String(counts.concepts || 0) }), el("span", { text: "基础概念" })]),
        el("div", { class: "stat" }, [el("b", { text: String(counts.advanced || 0) }), el("span", { text: "进阶专题" })]),
        el("div", { class: "stat" }, [el("b", { text: String(counts.classics || 0) }), el("span", { text: "2026 年前高影响论文" })]),
        el("div", { class: "stat" }, [el("b", { text: String(counts.papers || 0) }), el("span", { text: "领域论文 / 产品 / 标准" })]),
        el("div", { class: "stat" }, [el("b", { text: String(counts.ideas || 0) }), el("span", { text: "经查新评审的研究方向" })])
      ]),
      el("div", { class: "starts" }, [
        pageAnchor("roadmap.html", "start", [el("i", { text: "零基础" }), el("b", { text: "从学习路线开始" }), el("span", { text: "分阶段的概念、论文、课程和动手项目" })]),
        pageAnchor("guided.html", "start", [el("i", { text: "想读懂两篇论文" }), el("b", { text: "精读导读" }), el("span", { text: "逐步拆解 Quark 与 Ha et al.，每一步链接到所需的基础概念" })]),
        pageAnchor("ideas.html", "start", [el("i", { text: "找研究方向" }), el("b", { text: "研究机会" }), el("span", { text: "18 个经对抗查新与模拟评审的方向" })])
      ])
    ])
  ]);
  if (H.executive_summary_zh) addSection("summary", "执行摘要", [secHead("Executive summary", "执行摘要"), el("div", { class: "prose" }, paras(H.executive_summary_zh))]);

  // Site map: every page, grouped by part (the part introductions that used to head each part live here).
  (function () {
    var parts = [
      { group: "入门学习", eyebrow: "Part I · Learn", lede: meta.learn_lede || "" },
      { group: "领域调研", eyebrow: "Part II · Survey", lede: meta.survey_lede || "" },
      { group: "研究", eyebrow: "Part III · Research", lede: "" }
    ];
    var desc = H.pageDesc || {};
    addSection("sitemap", "内容导航", [
      secHead("Site map", "内容导航", "全站按“入门学习 / 领域调研 / 研究”三部分组织。左侧（手机上为顶部）导航栏可随时切换页面，每页底部有上一页 / 下一页。"),
      el("div", { class: "sitemap" }, parts.map(function (pt) {
        var pages = arr(SITE.pages).filter(function (p) { return p.group === pt.group; });
        return el("div", { class: "grp-card" }, [
          el("div", { class: "eyebrow", text: pt.eyebrow }),
          el("h3", { class: "sub", text: pt.group }),
          pt.lede ? el("p", { text: pt.lede }) : null,
          el("div", { class: "pages" }, pages.map(function (p) {
            return pageAnchor(p.href || p.file, "", [el("i", { text: p.alias ? "本页下方" : p.file }), el("b", { text: p.label }), el("span", { text: desc[p.key] || "" })]);
          }))
        ]);
      }))
    ]);
  })();

  addSection("method", "方法与说明", [secHead("Method & caveats", "调研方法与使用说明"), el("div", { class: "prose" }, paras(meta.method_zh || ""))]);
