  // ================= page: 分方向综述 + 论文库 =================
  var areas = arr(DATA.areas);
  var papers = arr(DATA.papers);
  var areaName = {}; areas.forEach(function (a) { areaName[a.key] = a.area_title_zh || a.key; });
  function shortLabel(t) { t = str(t).split(/[：（(]/)[0].trim(); return t.length > 18 ? t.slice(0, 17) + "…" : t; }
  var dbState = { q: "", area: "all", tier: "all", year: "all" };
  var dbRender = null;
  addSection("areas", "分方向综述", [
    secHead("Sub-areas", "分方向综述", "每个方向包含演进脉络、子主题、时间线、趋势与开放问题。点“查看本方向论文”跳到论文库并按方向筛选。"),
    el("div", { style: "display:grid;gap:12px" }, areas.map(function (a, idx) {
      var n = papers.filter(function (p) { return arr(p.areas).indexOf(a.key) >= 0; }).length;
      var d = el("details", { class: "area", id: "area-" + a.key }, [
        el("summary", null, [el("h3", { text: a.area_title_zh || a.key }), el("span", { class: "cnt", text: n + " 篇 · " + arr(a.subtopics).length + " 个子主题" }), el("span", { class: "tog" })]),
        el("div", { class: "area-body" }, [
          el("div", { class: "prose" }, paras(a.overview_zh)),
          el("div", { class: "subgrid" }, arr(a.subtopics).map(function (s) { return el("div", { class: "subcard" }, [el("b", { text: s.name_zh }), el("span", { class: "en", text: s.name_en }), el("p", { text: s.summary_zh }), arr(s.representative_works).length ? el("span", { class: "reps", text: "代表：" + arr(s.representative_works).join("；") }) : null]); })),
          arr(a.timeline).length ? el("div", { class: "blk" }, [el("h4", { text: "时间线" }), el("div", { class: "timeline" }, arr(a.timeline).slice().sort(function (x, y) { return (x.year || 0) - (y.year || 0); }).map(function (t) { return el("div", null, [el("span", { class: "y", text: String(t.year) }), el("span", { text: t.event_zh })]); }))]) : null,
          el("div", { class: "two" }, [el("div", { class: "blk" }, [el("h4", { text: "趋势" }), ul(a.trends_zh)]), el("div", { class: "blk" }, [el("h4", { text: "开放问题" }), ul(a.open_problems_zh)])]),
          a.relation_to_anchors_zh ? el("div", { class: "blk" }, [el("h4", { text: "与两篇锚点论文的关系" }), el("div", { class: "prose" }, paras(a.relation_to_anchors_zh))]) : null,
          el("button", { class: "btn", type: "button", text: "查看本方向论文 →", onclick: function () { dbState.area = a.key; var s = document.getElementById("db-area"); if (s) s.value = a.key; if (dbRender) dbRender(); goTo("papers"); } })
        ])
      ]);
      if (idx === 0) d.open = true;
      return d;
    }))
  ]);
  areas.forEach(function (a) { addTocItem("area-" + a.key, shortLabel(a.area_title_zh || a.key)); });

  (function () {
    var years = {}; papers.forEach(function (p) { if (p.year) years[p.year] = 1; });
    var yearList = Object.keys(years).map(Number).sort(function (a, b) { return b - a; });
    var q = el("input", { id: "db-q", type: "search", placeholder: "标题、作者、摘要关键词…", "aria-label": "搜索论文" });
    var sa = el("select", { id: "db-area", "aria-label": "方向" }, [el("option", { value: "all", text: "全部方向" })].concat(areas.map(function (a) { return el("option", { value: a.key, text: a.area_title_zh || a.key }); })));
    var stt = el("select", { id: "db-tier", "aria-label": "重要性" }, [["all", "全部"], ["milestone", "里程碑"], ["important", "重要"], ["relevant", "相关"]].map(function (o) { return el("option", { value: o[0], text: o[1] }); }));
    var sy = el("select", { id: "db-year", "aria-label": "年份" }, [el("option", { value: "all", text: "全部年份" }), el("option", { value: "2025+", text: "2025 年及以后" }), el("option", { value: "2023+", text: "2023 年及以后" })].concat(yearList.map(function (y) { return el("option", { value: String(y), text: String(y) }); })));
    var count = el("span", { class: "db-count mono" });
    var tbody = el("tbody");
    var tierLabel = { milestone: "里程碑", important: "重要", relevant: "相关" };
    var tierRank = { milestone: 0, important: 1, relevant: 2 };
    function match(p) {
      if (dbState.area !== "all" && arr(p.areas).indexOf(dbState.area) < 0) return false;
      if (dbState.tier !== "all" && p.tier !== dbState.tier) return false;
      if (dbState.year === "2025+" && !(p.year >= 2025)) return false;
      else if (dbState.year === "2023+" && !(p.year >= 2023)) return false;
      else if (/^\d{4}$/.test(dbState.year) && String(p.year) !== dbState.year) return false;
      if (dbState.q) { var hay = (p.title + " " + p.authors + " " + p.venue + " " + p.summary_zh + " " + p.key_numbers).toLowerCase(); if (hay.indexOf(dbState.q) < 0) return false; }
      return true;
    }
    function render() {
      var rows = papers.filter(match).sort(function (a, b) { return (b.year || 0) - (a.year || 0) || (tierRank[a.tier] - tierRank[b.tier]); });
      count.textContent = rows.length + " / " + papers.length + " 条";
      tbody.textContent = "";
      var frag = document.createDocumentFragment();
      rows.forEach(function (p) {
        frag.appendChild(el("tr", null, [
          el("td", { class: "y", text: String(p.year || "") }),
          el("td", { class: "t" }, [link(p.title, p.url), el("small", { text: [p.authors, p.venue].filter(Boolean).join(" · ") })]),
          el("td", null, [el("span", { class: "tier " + (p.tier || "relevant"), text: tierLabel[p.tier] || "相关" })].concat(arr(p.areas).map(function (k) { return el("span", { class: "areatag", text: areaName[k] || k }); }))),
          el("td", { class: "s", text: p.summary_zh || "" }),
          el("td", { class: "n", text: p.key_numbers || "" })
        ]));
      });
      tbody.appendChild(frag);
    }
    dbRender = render;
    q.addEventListener("input", function () { dbState.q = q.value.trim().toLowerCase(); render(); });
    sa.addEventListener("change", function () { dbState.area = sa.value; render(); });
    stt.addEventListener("change", function () { dbState.tier = stt.value; render(); });
    sy.addEventListener("change", function () { dbState.year = sy.value; render(); });
    addSection("papers", "论文库", [
      secHead("Paper database", "论文 / 产品 / 标准库", "按方向、重要性、年份筛选，按年份倒序。同一篇工作出现在多个方向时会合并并标注全部方向。"),
      el("div", { class: "db-controls" }, [el("label", { class: "field", for: "db-q" }, ["搜索", q]), el("label", { class: "field", for: "db-area" }, ["方向", sa]), el("label", { class: "field", for: "db-tier" }, ["重要性", stt]), el("label", { class: "field", for: "db-year" }, ["年份", sy]), count]),
      el("div", { class: "db-wrap" }, [el("table", { class: "db" }, [el("thead", null, [el("tr", null, ["年份", "工作", "标签", "简介", "关键数字"].map(function (h) { return el("th", { text: h }); }))]), tbody])])
    ]);
    render();
  })();
