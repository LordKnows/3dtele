  // ================= page: 术语表 =================
  var glossary = arr(DATA.glossary);
  // ---------- Glossary ----------
  if (glossary.length) {
    (function () {
      var cats = []; glossary.forEach(function (t) { if (t.category && cats.indexOf(t.category) < 0) cats.push(t.category); });
      var q = el("input", { id: "gl-q", type: "search", placeholder: "中英文术语或缩写…", "aria-label": "搜索术语" });
      var sc = el("select", { id: "gl-cat", "aria-label": "类别" }, [el("option", { value: "all", text: "全部类别" })].concat(cats.map(function (c) { return el("option", { value: c, text: c }); })));
      var count = el("span", { class: "db-count mono" });
      var tbody = el("tbody");
      var sorted = glossary.slice().sort(function (a, b) { return str(a.term_en).toLowerCase() < str(b.term_en).toLowerCase() ? -1 : 1; });
      function render() {
        var qq = q.value.trim().toLowerCase(), cc = sc.value;
        var rows = sorted.filter(function (t) { if (cc !== "all" && t.category !== cc) return false; if (!qq) return true; return (str(t.term_en) + " " + str(t.term_zh) + " " + str(t.abbr) + " " + str(t.def_zh)).toLowerCase().indexOf(qq) >= 0; });
        count.textContent = rows.length + " / " + glossary.length + " 条";
        tbody.textContent = "";
        var frag = document.createDocumentFragment();
        rows.forEach(function (t) { frag.appendChild(el("tr", null, [el("td", { class: "en" }, [t.term_en, t.abbr ? el("span", { class: "mono", style: "color:var(--muted);font-size:12px", text: " (" + t.abbr + ")" }) : null]), el("td", { class: "zh", text: t.term_zh }), el("td", { class: "def", text: t.def_zh }), el("td", null, [cChip(t.concept_id, true)])])); });
        tbody.appendChild(frag);
      }
      q.addEventListener("input", render); sc.addEventListener("change", render);
      render();
      addSection("glossary", "术语表", [
        secHead("Glossary", "术语表", "读论文时遇到的缩写和术语。点右侧概念可跳到对应的基础知识卡片。"),
        el("div", { class: "db-controls" }, [el("label", { class: "field", for: "gl-q" }, ["搜索", q]), el("label", { class: "field", for: "gl-cat" }, ["类别", sc]), count]),
        el("div", { class: "gl-wrap" }, [el("table", { class: "gl" }, [el("thead", null, [el("tr", null, ["English", "中文", "释义", "概念"].map(function (h) { return el("th", { text: h }); }))]), tbody])])
      ]);
    })();
  }
