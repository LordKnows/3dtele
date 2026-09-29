  // ================= tool: filterable paper database =================
  SLOTS.database = function () {
    var papers = arr(DATA.papers), names = DATA.areaNames || {};
    var areaKeys = Object.keys(names);
    var tierLabel = { milestone: "里程碑", important: "重要", relevant: "相关" }, tierRank = { milestone: 0, important: 1, relevant: 2 };
    var years = {};
    papers.forEach(function (p) { if (p.year) years[p.year] = 1; });
    var st = { q: "", area: "all", tier: "all", year: "all" };
    // ?area=<key> (from a sub-area page) preselects that area.
    var m = /[?&]area=([A-Za-z0-9._-]+)/.exec(window.location.search);
    if (m && names[m[1]]) st.area = m[1];
    var q = el("input", { id: "db-q", type: "search", placeholder: "标题、作者、摘要关键词…", autocomplete: "off" });
    var sa = el("select", { id: "db-area" }, [el("option", { value: "all", text: "全部方向" })].concat(areaKeys.map(function (k) { return el("option", { value: k, text: names[k] }); })));
    var stt = el("select", { id: "db-tier" }, [["all", "全部"], ["milestone", "里程碑"], ["important", "重要"], ["relevant", "相关"]].map(function (o) { return el("option", { value: o[0], text: o[1] }); }));
    var sy = el("select", { id: "db-year" }, [el("option", { value: "all", text: "全部年份" }), el("option", { value: "2025+", text: "2025 年及以后" }), el("option", { value: "2023+", text: "2023 年及以后" })]
      .concat(Object.keys(years).map(Number).sort(function (a, b) { return b - a; }).map(function (y) { return el("option", { value: String(y), text: String(y) }); })));
    sa.value = st.area;
    var count = el("span", { class: "count", "aria-live": "polite" });
    var tbody = el("tbody");
    function match(p) {
      if (st.area !== "all" && arr(p.areas).indexOf(st.area) < 0) return false;
      if (st.tier !== "all" && p.tier !== st.tier) return false;
      if (st.year === "2025+" && !(p.year >= 2025)) return false;
      if (st.year === "2023+" && !(p.year >= 2023)) return false;
      if (/^\d{4}$/.test(st.year) && String(p.year) !== st.year) return false;
      if (st.q && (str(p.title) + " " + str(p.authors) + " " + str(p.venue) + " " + str(p.summary_zh) + " " + str(p.key_numbers)).toLowerCase().indexOf(st.q) < 0) return false;
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
          el("td", { class: "tags" }, [el("span", { class: "tier " + (p.tier || "relevant"), text: tierLabel[p.tier] || "相关" })]
            .concat(arr(p.areas).map(function (k) { return el("span", { class: "area", text: names[k] || k }); }))),
          el("td", { class: "s", text: p.summary_zh || "" }),
          el("td", { class: "n", text: p.key_numbers || "" })
        ]));
      });
      tbody.appendChild(frag);
    }
    q.addEventListener("input", function () { st.q = q.value.trim().toLowerCase(); render(); });
    sa.addEventListener("change", function () { st.area = sa.value; render(); });
    stt.addEventListener("change", function () { st.tier = stt.value; render(); });
    sy.addEventListener("change", function () { st.year = sy.value; render(); });
    render();
    return el("div", { class: "tool fullwidth" }, [
      el("div", { class: "filters" }, [el("label", { for: "db-q" }, ["搜索", q]), el("label", { for: "db-area" }, ["方向", sa]),
        el("label", { for: "db-tier" }, ["重要性", stt]), el("label", { for: "db-year" }, ["年份", sy]), count]),
      el("div", { class: "table-wrap" }, [el("table", { class: "booktabs db" }, [
        el("thead", null, [el("tr", null, ["年份", "工作", "标签", "简介", "关键数字"].map(function (h) { return el("th", { text: h }); }))]), tbody
      ])])
    ]);
  };
