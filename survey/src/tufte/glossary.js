  // ================= tool: searchable glossary =================
  SLOTS.glossary = function () {
    var terms = arr(DATA.glossary);
    var cats = [];
    terms.forEach(function (t) { if (t.cat && cats.indexOf(t.cat) < 0) cats.push(t.cat); });
    var q = el("input", { id: "gl-q", type: "search", placeholder: "中英文术语或缩写…", autocomplete: "off" });
    var sc = el("select", { id: "gl-cat" }, [el("option", { value: "all", text: "全部类别" })].concat(cats.map(function (c) { return el("option", { value: c, text: c }); })));
    var count = el("span", { class: "count", "aria-live": "polite" });
    var tbody = el("tbody");
    var rows = terms.slice().sort(function (a, b) { return str(a.en).toLowerCase() < str(b.en).toLowerCase() ? -1 : 1; }).map(function (t) {
      var tr = el("tr", { id: t.id }, [
        el("td", { class: "en" }, [t.en, t.abbr ? el("span", { class: "abbr", text: " (" + t.abbr + ")" }) : null]),
        el("td", { class: "zh", text: t.zh }),
        el("td", { class: "def", text: t.def }),
        el("td", { class: "c" }, [t.k && hasX(t.k) ? xlink(t.k, XREF[t.k].t) : null])
      ]);
      tr._hay = (str(t.en) + " " + str(t.zh) + " " + str(t.abbr) + " " + str(t.def)).toLowerCase();
      tr._cat = t.cat;
      tbody.appendChild(tr);
      return tr;
    });
    function apply() {
      var qq = q.value.trim().toLowerCase(), cc = sc.value, n = 0;
      rows.forEach(function (tr) {
        var ok = (cc === "all" || tr._cat === cc) && (!qq || tr._hay.indexOf(qq) >= 0);
        tr.hidden = !ok;
        if (ok) n++;
      });
      count.textContent = n + " / " + terms.length + " 条";
    }
    q.addEventListener("input", apply);
    sc.addEventListener("change", apply);
    apply();
    return el("div", { class: "tool fullwidth" }, [
      el("div", { class: "filters" }, [el("label", { for: "gl-q" }, ["搜索", q]), el("label", { for: "gl-cat" }, ["类别", sc]), count]),
      el("div", { class: "table-wrap" }, [el("table", { class: "booktabs gl" }, [
        el("thead", null, [el("tr", null, ["English", "中文", "释义", "概念"].map(function (h) { return el("th", { text: h }); }))]), tbody
      ])])
    ]);
  };
