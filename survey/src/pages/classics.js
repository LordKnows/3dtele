  // ================= page: 经典论文 + 前沿阅读清单 =================
  var classics = arr(DATA.classics);
  var L = { themes: arr(DATA.themes) };
  var themeName = {}; L.themes.forEach(function (t) { themeName[t.id] = t.title_zh; });
  var synth = { reading_path: arr(DATA.reading_path) };
  // ---------- Classics ----------
  if (classics.length) {
    (function () {
      var themes = arr(L.themes);
      var st = { theme: "all", must: "all", diff: "all", sort: "year" };
      var tip = el("div", { class: "vtip", hidden: "" });
      function laneChart() {
        var W = 940, left = 170, right = 16, top = 26;
        var x0 = left, x1 = W - right, split = 2010;
        var xBreak = x0 + (x1 - x0) * 0.34;
        var minYear = classics.reduce(function (m, p) { return p.year ? Math.min(m, p.year) : m; }, 2009);
        var y0 = Math.floor((minYear - 1) / 5) * 5;
        function xs(y) { y = Math.max(y0, Math.min(2025.6, y)); return y < split ? x0 + 6 + (y - y0) / (split - y0) * (xBreak - x0 - 18) : xBreak + (y - split + 0.5) / (2025.6 - split + 0.5) * (x1 - xBreak); }
        function rr(c) { var n = Math.max(1, Number(c) || 1); return Math.max(3.5, Math.min(8, 1.8 * Math.log10(n) - 0.6)); }
        var shortLane = { "t-ibr-geometry": "经典 IBR 与多视几何", "t-fusion-capture": "深度融合与临场系统", "t-deep-geometry": "深度学习几何", "t-neural-rendering": "神经渲染与新视角合成", "t-dynamic-human": "动态场景、4D 与人体", "t-generative-ff": "生成先验、前馈与评测" };
        var laneData = themes.map(function (t) { return { t: t, items: [] }; });
        var laneIdx = {}; themes.forEach(function (t, i) { laneIdx[t.id] = i; });
        classics.forEach(function (p, i) { var li = laneIdx[p.theme]; if (li === undefined) return; laneData[li].items.push(i); });
        var y = top, lanes = [];
        laneData.forEach(function (ld) {
          var byYear = {};
          ld.items.forEach(function (i) { var yr = classics[i].year || 0; (byYear[yr] = byYear[yr] || []).push(i); });
          var maxStack = 1; Object.keys(byYear).forEach(function (k) { maxStack = Math.max(maxStack, Math.ceil(byYear[k].length / 2)); });
          var h = Math.max(44, maxStack * 22 + 14);
          lanes.push({ ld: ld, y: y, h: h, byYear: byYear }); y += h;
        });
        var H = y + 30;
        var svg = sv("svg", { class: "lanes", viewBox: "0 0 " + W + " " + H, role: "img", "aria-label": "2026 年前高影响论文时间分布（按主题分泳道）" });
        [y0, y0 + 10, y0 + 20].filter(function (yr) { return yr < split - 4; }).forEach(function (yr) { svg.appendChild(sv("line", { class: "grid", x1: xs(yr), x2: xs(yr), y1: top - 6, y2: H - 26 })); svg.appendChild(sv("text", { class: "axis", x: xs(yr), y: H - 10, "text-anchor": "middle", text: String(yr) })); });
        for (var yr = 2010; yr <= 2025; yr += 3) { svg.appendChild(sv("line", { class: "grid", x1: xs(yr), x2: xs(yr), y1: top - 6, y2: H - 26 })); svg.appendChild(sv("text", { class: "axis", x: xs(yr), y: H - 10, "text-anchor": "middle", text: String(yr) })); }
        svg.appendChild(sv("path", { class: "brk", d: "M" + (xBreak - 6) + "," + (H - 30) + " l4,-8 M" + (xBreak - 1) + "," + (H - 30) + " l4,-8" }));
        svg.appendChild(sv("text", { class: "axis", x: (x0 + xBreak) / 2, y: top - 12, "text-anchor": "middle", text: y0 + "–2009（压缩比例）" }));
        svg.appendChild(sv("text", { class: "axis", x: (xBreak + x1) / 2, y: top - 12, "text-anchor": "middle", text: "2010–2025" }));
        lanes.forEach(function (ln, li) {
          if (li > 0) svg.appendChild(sv("line", { class: "grid", x1: 0, x2: W, y1: ln.y, y2: ln.y }));
          var lab = shortLane[ln.ld.t.id] || str(ln.ld.t.title_zh).replace(/（.*?）/, "");
          svg.appendChild(sv("text", { class: "lane-l", x: 4, y: ln.y + ln.h / 2 + 4, text: lab.length > 13 ? lab.slice(0, 12) + "…" : lab }));
          if (!ln.ld.items.length) svg.appendChild(sv("text", { class: "axis", x: xBreak + 8, y: ln.y + ln.h / 2 + 4, text: "（本主题暂无数据）" }));
          Object.keys(ln.byYear).forEach(function (k) {
            var list = ln.byYear[k].slice().sort(function (a, b) { return (classics[b].citations || 0) - (classics[a].citations || 0); });
            var rows = Math.ceil(list.length / 2);
            list.forEach(function (i, j) {
              var p = classics[i];
              var col = list.length > 1 ? (j % 2 === 0 ? -1 : 1) : 0, row = Math.floor(j / 2);
              var cx = xs(Number(k)) + col * 6, cy = ln.y + ln.h / 2 + (row - (rows - 1) / 2) * 22;
              var r = rr(p.citations);
              var g = sv("g", { class: "m", tabindex: "0", role: "button", "aria-label": p.title + "，" + p.year + "，引用 " + fmtCit(p.citations) });
              g.appendChild(sv("circle", { class: "hit", cx: cx, cy: cy, r: r + 5 }));
              g.appendChild(sv("circle", { class: "dot" + (p.must_read ? "" : " hollow"), cx: cx, cy: cy, r: r }));
              function showTip() {
                tip.textContent = "";
                tip.appendChild(el("b", { text: p.title }));
                tip.appendChild(el("small", { text: [p.year, p.venue, "引用 " + fmtCit(p.citations)].filter(Boolean).join(" · ") }));
                tip.appendChild(el("span", { text: p.must_read ? "必读 · 点击查看" : "点击查看" }));
                tip.hidden = false;
                var wrap = tip.parentElement, wr = wrap.getBoundingClientRect(), sr = svg.getBoundingClientRect();
                var scale = sr.width / W;
                var px = sr.left - wr.left + wrap.scrollLeft + cx * scale, py = sr.top - wr.top + cy * scale;
                var tw = tip.offsetWidth;
                tip.style.left = Math.max(4, Math.min(px + 12, wrap.scrollWidth - tw - 4)) + "px";
                tip.style.top = (py + 14) + "px";
              }
              g.addEventListener("mouseenter", showTip); g.addEventListener("focus", showTip);
              g.addEventListener("mouseleave", function () { tip.hidden = true; }); g.addEventListener("blur", function () { tip.hidden = true; });
              g.addEventListener("click", function () { tip.hidden = true; st.theme = "all"; st.must = "all"; st.diff = "all"; syncControls(); renderList(); goTo("classic-" + i); });
              g.addEventListener("keydown", function (e) { if (e.key === "Enter" || e.key === " ") { e.preventDefault(); goTo("classic-" + i); } });
              svg.appendChild(g);
            });
          });
        });
        var legend = el("div", { class: "legend" }, [
          el("span", null, [lgDot(false), " 必读"]), el("span", null, [lgDot(true), " 其他"]),
          el("span", { text: "点的大小 ∝ log(引用数)；悬停看详情，点击跳到条目" })
        ]);
        return el("div", { class: "lanes-wrap" }, [svg, legend, tip]);
      }
      function lgDot(hollow) { var s = sv("svg", { width: "14", height: "14", viewBox: "0 0 14 14", "aria-hidden": "true" }); s.appendChild(sv("circle", { cx: 7, cy: 7, r: 5, style: hollow ? "fill:var(--surface);stroke:var(--accent);stroke-width:1.6" : "fill:var(--accent)" })); return s; }
      var listHost = el("div", { class: "classic-list" });
      var count = el("span", { class: "db-count mono" });
      var sTheme = el("select", { id: "cl-theme", "aria-label": "主题" }, [el("option", { value: "all", text: "全部主题" })].concat(themes.map(function (t) { return el("option", { value: t.id, text: t.title_zh }); })));
      var sMust = el("select", { id: "cl-must", "aria-label": "必读" }, [["all", "全部"], ["must", "只看必读"]].map(function (o) { return el("option", { value: o[0], text: o[1] }); }));
      var sDiff = el("select", { id: "cl-diff", "aria-label": "难度" }, [["all", "全部难度"], ["入门", "入门"], ["进阶", "进阶"], ["专家", "专家"]].map(function (o) { return el("option", { value: o[0], text: o[1] }); }));
      var sSort = el("select", { id: "cl-sort", "aria-label": "排序" }, [["year", "按年份"], ["cit", "按引用数"]].map(function (o) { return el("option", { value: o[0], text: o[1] }); }));
      function syncControls() { sTheme.value = st.theme; sMust.value = st.must; sDiff.value = st.diff; sSort.value = st.sort; }
      function renderList() {
        var idx = classics.map(function (_, i) { return i; }).filter(function (i) {
          var p = classics[i];
          if (st.theme !== "all" && arr(p.themes).indexOf(st.theme) < 0 && p.theme !== st.theme) return false;
          if (st.must === "must" && !p.must_read) return false;
          if (st.diff !== "all" && p.difficulty !== st.diff) return false;
          return true;
        });
        idx.sort(function (a, b) { var A = classics[a], B = classics[b]; return st.sort === "cit" ? (B.citations || 0) - (A.citations || 0) : (A.year || 0) - (B.year || 0) || (B.citations || 0) - (A.citations || 0); });
        count.textContent = idx.length + " / " + classics.length + " 篇";
        listHost.textContent = "";
        idx.forEach(function (i) {
          var p = classics[i];
          listHost.appendChild(el("details", { class: "classic", id: "classic-" + i }, [
            el("summary", null, [
              el("span", { class: "yr", text: String(p.year || "") }),
              el("div", { class: "ti" }, [el("b", { text: p.title }), el("small", { text: [p.authors, p.venue].filter(Boolean).join(" · ") })]),
              el("span", { class: "cit" }, [p.must_read ? el("span", { class: "pill must", text: "必读" }) : null, " ", "引用 " + fmtCit(p.citations)])
            ]),
            el("div", { class: "classic-body" }, [
              el("div", { class: "chips" }, [link("打开论文 ↗", p.url), el("span", { class: "chip", text: themeName[p.theme] || p.theme || "" }), p.difficulty ? el("span", { class: "chip", text: "难度：" + p.difficulty }) : null, el("span", { class: "chip", text: (p.citations_source || "") + (p.citations >= 0 ? " 引用 " + p.citations : "") })]),
              textBlk("为什么有影响力", p.influence_zh),
              textBlk("主要贡献", p.contributions_zh),
              textBlk("与两篇锚点论文的联系", p.anchor_link_zh),
              chipRow("相关概念", arr(p.concept_ids).map(function (c) { return cChip(c, true); })),
              chipRow("进阶专题", arr(p.adv_ids).map(aChip))
            ])
          ]));
        });
      }
      sTheme.addEventListener("change", function () { st.theme = sTheme.value; renderList(); });
      sMust.addEventListener("change", function () { st.must = sMust.value; renderList(); });
      sDiff.addEventListener("change", function () { st.diff = sDiff.value; renderList(); });
      sSort.addEventListener("change", function () { st.sort = sSort.value; renderList(); });
      renderList();
      addSection("classics", "经典论文", [
        secHead("Pre-2026 classics", "2026 年之前的高影响论文", meta.classics_lede || ""),
        laneChart(),
        el("div", { class: "db-controls" }, [el("label", { class: "field", for: "cl-theme" }, ["主题", sTheme]), el("label", { class: "field", for: "cl-must" }, ["必读", sMust]), el("label", { class: "field", for: "cl-diff" }, ["难度", sDiff]), el("label", { class: "field", for: "cl-sort" }, ["排序", sSort]), count]),
        listHost
      ]);
    })();
  }

  if (arr(synth.reading_path).length) {
    addSection("reading", "前沿阅读清单", [
      secHead("Reading list", "前沿阅读清单", "按入门 / 进阶 / 前沿三档列出的领域论文（偏 2024–2026），与上面的经典论文互补。"),
      el("div", { class: "path" }, arr(synth.reading_path).map(function (s) { return el("div", { class: "panel" }, [el("h3", { class: "sub", text: s.stage_zh, style: "margin-bottom:10px" }), el("ol", null, arr(s.items).map(function (x) { return el("li", null, [link(x.title, x.url), el("small", { text: x.why_zh })]); }))]); }))
    ]);
  }
