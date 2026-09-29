  // ================= slot: classic papers on a timeline, one lane per theme =================
  // DATA.chart = {lanes: [{id, label}], points: [{y: year, c: citations, m: must-read, t: title, v: venue, u: url, lane}]}
  SLOTS["classics-chart"] = function () {
    var C = DATA.chart || {}, lanes = arr(C.lanes), pts = arr(C.points);
    if (!pts.length) return null;
    var W = 940, left = lanes.length > 1 ? 170 : 16, right = 16, top = 26, split = 2010;
    var x0 = left, x1 = W - right, xBreak = x0 + (x1 - x0) * 0.34;
    var minYear = pts.reduce(function (m, p) { return p.y ? Math.min(m, p.y) : m; }, 2009);
    var y0 = Math.floor((minYear - 1) / 5) * 5;
    function xs(y) { y = Math.max(y0, Math.min(2025.6, y)); return y < split ? x0 + 6 + (y - y0) / (split - y0) * (xBreak - x0 - 18) : xBreak + (y - split + 0.5) / (2025.6 - split + 0.5) * (x1 - xBreak); }
    function rr(c) { var n = Math.max(1, Number(c) || 1); return Math.max(3.5, Math.min(8, 1.8 * Math.log10(n) - 0.6)); }
    var y = top, rows = [];
    lanes.forEach(function (ln) {
      var byYear = {};
      pts.forEach(function (p) { if (p.lane === ln.id) (byYear[p.y] = byYear[p.y] || []).push(p); });
      var maxStack = 1;
      Object.keys(byYear).forEach(function (k) { maxStack = Math.max(maxStack, Math.ceil(byYear[k].length / 2)); });
      var h = Math.max(44, maxStack * 22 + 14);
      rows.push({ ln: ln, y: y, h: h, byYear: byYear });
      y += h;
    });
    var Ht = y + 30;
    var svg = sv("svg", { class: "lanes", viewBox: "0 0 " + W + " " + Ht, role: "img", "aria-label": "经典论文时间分布" + (lanes.length > 1 ? "（按主题分泳道）" : "") });
    function tick(yr) {
      svg.appendChild(sv("line", { class: "grid", x1: xs(yr), x2: xs(yr), y1: top - 6, y2: Ht - 26 }));
      svg.appendChild(sv("text", { class: "axis", x: xs(yr), y: Ht - 10, "text-anchor": "middle", text: String(yr) }));
    }
    [y0, y0 + 10, y0 + 20].filter(function (yr) { return yr < split - 4; }).forEach(tick);
    for (var yr = 2010; yr <= 2025; yr += 3) tick(yr);
    svg.appendChild(sv("path", { class: "brk", d: "M" + (xBreak - 6) + "," + (Ht - 30) + " l4,-8 M" + (xBreak - 1) + "," + (Ht - 30) + " l4,-8" }));
    svg.appendChild(sv("text", { class: "axis", x: (x0 + xBreak) / 2, y: top - 12, "text-anchor": "middle", text: y0 + "–2009（压缩比例）" }));
    svg.appendChild(sv("text", { class: "axis", x: (xBreak + x1) / 2, y: top - 12, "text-anchor": "middle", text: "2010–2025" }));
    var tip = el("div", { class: "vtip", hidden: "" });
    rows.forEach(function (r, li) {
      if (li > 0) svg.appendChild(sv("line", { class: "grid", x1: 0, x2: W, y1: r.y, y2: r.y }));
      if (lanes.length > 1) svg.appendChild(sv("text", { class: "lane-l", x: 4, y: r.y + r.h / 2 + 4, text: r.ln.label }));
      Object.keys(r.byYear).forEach(function (k) {
        var list = r.byYear[k].slice().sort(function (a, b) { return (b.c || 0) - (a.c || 0); });
        var nrow = Math.ceil(list.length / 2);
        list.forEach(function (p, j) {
          var col = list.length > 1 ? (j % 2 === 0 ? -1 : 1) : 0, row = Math.floor(j / 2);
          var cx = xs(Number(k)) + col * 6, cy = r.y + r.h / 2 + (row - (nrow - 1) / 2) * 22;
          var a = sv("a", { class: "m", "aria-label": p.t + "，" + p.y + "，引用 " + fmtCit(p.c) }, [
            sv("circle", { class: "hit", cx: cx, cy: cy, r: rr(p.c) + 5 }),
            sv("circle", { class: "dot" + (p.m ? "" : " hollow"), cx: cx, cy: cy, r: rr(p.c) })
          ]);
          var h = relHref(p.u);
          if (h) a.setAttribute("href", h);
          function show() {
            tip.textContent = "";
            tip.appendChild(el("b", { text: p.t }));
            tip.appendChild(el("small", { text: [p.y, p.v, "引用 " + fmtCit(p.c)].filter(Boolean).join(" · ") }));
            if (p.m) tip.appendChild(el("span", { text: "必读" }));
            tip.hidden = false;
            var wrap = tip.parentElement, wr = wrap.getBoundingClientRect(), sr = svg.getBoundingClientRect(), scale = sr.width / W;
            var px = sr.left - wr.left + wrap.scrollLeft + cx * scale, py = sr.top - wr.top + cy * scale;
            tip.style.left = Math.max(4, Math.min(px + 12, wrap.scrollWidth - tip.offsetWidth - 4)) + "px";
            tip.style.top = (py + 14) + "px";
          }
          a.addEventListener("mouseenter", show);
          a.addEventListener("focus", show);
          a.addEventListener("mouseleave", function () { tip.hidden = true; });
          a.addEventListener("blur", function () { tip.hidden = true; });
          svg.appendChild(a);
        });
      });
    });
    function lgDot(hollow) {
      var s = sv("svg", { width: "12", height: "12", viewBox: "0 0 12 12", "aria-hidden": "true" });
      s.appendChild(sv("circle", { class: "dot" + (hollow ? " hollow" : ""), cx: 6, cy: 6, r: 4 }));
      return s;
    }
    return el("figure", { class: "fullwidth chart-fig" }, [
      el("div", { class: "lanes-wrap" }, [svg, tip]),
      el("figcaption", null, [lgDot(false), " 必读　", lgDot(true), " 其他　点的大小 ∝ log(引用数)；悬停看详情，点击跳到条目"])
    ]);
  };
