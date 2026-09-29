  // ================= article: a page composed as blocks in routes.py =================
  (function () {
    var PG = DATA.page || {};
    var H = PG.head || {};
    if (PG.id) art.id = PG.id;

    // A link dict from routes.py: {k} an entry with hover preview, {u, t} a page of this site, {url, t} an external page.
    function part(x) {
      if (x === null || x === undefined) return null;
      if (typeof x === "string") return x;
      if (x.k) return xlink(x.k, x.t || null);
      if (x.u) return pageLink(x.u, x.t || x.u);
      if (x.url) return link(x.t || x.url, x.url);
      return x.t ? str(x.t) : null;
    }
    function noteNodes(n) {
      var kids = [noteLabel(n.label)];
      if (n.t) kids = kids.concat(rich(n.t));
      arr(n.links).forEach(function (l, i) { if (i) kids.push(el("br")); kids.push(part(l)); });
      return kids;
    }
    function runIn(label) { return el("b", { class: "run-in", text: label + "：" }); }
    function multiline(text) {
      var out = [];
      str(text).split("\n").forEach(function (line, i) { if (i) out.push(el("br")); out = out.concat(rich(line)); });
      return out;
    }

    // ---------- head ----------
    var meta = [];
    if (arr(H.prereqs).length) {
      meta.push(marginnote([noteLabel("阅读前需要")].concat(arr(H.prereqs).map(function (p, i) {
        var a = part(p);
        return i ? el("span", null, ["；", a]) : a;
      }))));
    }
    var sep = false;
    arr(H.meta).concat(H.minutes > 1 ? ["约 " + H.minutes + " 分钟"] : []).forEach(function (x) {
      var n = part(x);
      if (!n || (typeof n === "string" && !n.trim())) return;
      if (sep) meta.push(" · ");
      meta.push(n);
      sep = !(typeof x === "string" && /：$/.test(x));
    });
    articleHead({ title: H.title, subtitle: H.sub, meta: meta.length ? meta : null, epigraph: H.epigraph });
    if (str(H.lede).trim()) art.appendChild(el("div", { class: "lede" }, paras(H.lede)));

    // ---------- blocks ----------
    function heading(tag, b) {
      var title = b.url && safeUrl(b.url) ? link(b.t, b.url) : (b.k ? part({ k: b.k, t: b.t }) : str(b.t));
      var h = el(tag, { id: b.id || null }, [title]);
      if (b.sn) h.appendChild(sidenote(noteNodes(b.sn)));
      if (b.en) h.appendChild(el("span", { class: "en", text: b.en }));
      if (b.tag) h.appendChild(el("span", { class: "used", text: b.tag }));
      return h;
    }
    function withNotes(nodes, b) {
      if (nodes.length && b.mn) nodes[0].insertBefore(marginnote(noteNodes(b.mn)), nodes[0].firstChild);
      if (nodes.length && b.label) nodes[0].insertBefore(runIn(b.label), nodes[0].firstChild);
      return nodes;
    }
    function listItem(x) {
      if (typeof x === "string") return el("li", null, rich(x));
      return el("li", null, (x.label ? [runIn(x.label)] : []).concat(rich(x.t)));
    }
    function refsList(items, cls) {
      var left = items.some(function (x) { return x.left; });
      return el("ul", { class: "refs " + (cls || "") + (left ? "" : " noleft") }, items.map(function (x) {
        var body = [x.k || x.u || x.url ? part(x) : el("span", { class: "plain-t", text: x.t })];
        if (x.tag) body.push(el("span", { class: "used", text: x.tag }));
        if (x.sub) body.push(el("div", { class: "en", text: x.sub }));
        if (str(x.gloss).trim()) body.push(el("div", { class: "gloss" }, multiline(x.gloss)));
        var kids = left ? [el("span", { class: /^\d{4}$/.test(str(x.left)) ? "yr" : "kind", text: str(x.left) })] : [];
        return el("li", { id: x.id || null }, kids.concat([el("div", null, body)]));
      }));
    }
    var TY = { book: "教材", course: "课程", paper: "论文", tutorial: "教程", code: "代码", video: "视频", blog: "文章" };
    function tocGroups(groups, level) {
      var out = [];
      arr(groups).forEach(function (g) {
        if (g.h) out.push(el(level, { class: "toc-h" }, [g.k || g.u ? part({ k: g.k, u: g.u, t: g.h }) : g.h]));
        if (str(g.lede).trim()) out.push(el("p", { class: "toc-lede" }, rich(g.lede)));
        out.push(el("ol", { class: "toc" }, arr(g.items).map(function (it) {
          return el("li", null, [
            el("div", { class: "toc-t" }, [part({ k: it.k, u: it.u, t: it.t }), it.en ? el("span", { class: "en", text: it.en }) : null,
              it.meta ? el("span", { class: "toc-meta", text: it.meta }) : null]),
            str(it.s).trim() ? el("p", { class: "toc-s", text: it.s }) : null
          ]);
        })));
      });
      return out;
    }
    function cell(tag, c) { return el(tag, null, c && typeof c === "object" ? [part(c)] : rich(c)); }

    var box = null;
    function cur() { if (!box) { box = el("section"); art.appendChild(box); } return box; }
    function render(b) {
      switch (b.b) {
        case "p": return withNotes(paras(b.t), b);
        case "lines": return withNotes(lines(b.t), b);
        case "h3": return [heading("h3", b)];
        case "note": return [el("p", { class: "note", text: b.t })];
        case "ul": case "ol": return [el(b.b, null, arr(b.items).map(listItem))];
        case "eqs": return [eqList(b.eqs)];
        case "qa": return [el("p", { class: "quiz-h", text: "自测" }), el("ol", { class: "quiz" }, arr(b.items).map(function (q) {
          return el("li", null, [el("p", null, rich(q.q)), el("details", null, [el("summary", { text: "答案" }), el("p", null, rich(q.a))])]);
        }))];
        case "res": return [refsList(arr(b.items).map(function (r) {
          return { left: TY[r.type] || r.type || "", url: r.url, t: r.title, gloss: r.note_zh };
        }))];
        case "refs": return [refsList(arr(b.items), b.cls)];
        case "toc": return tocGroups(b.groups, cur().querySelector("h2") ? "h3" : "h2");
        case "table": return [el("div", { class: "table-wrap" + (b.wide ? " fullwidth" : "") }, [el("table", { class: "booktabs" + (b.cls ? " " + b.cls : "") }, [
          el("thead", null, [el("tr", null, arr(b.head).map(function (h) { return el("th", { text: h }); }))]),
          el("tbody", null, arr(b.rows).map(function (r) { return el("tr", null, arr(r).map(function (c) { return cell("td", c); })); }))
        ])])];
        case "timeline": return [el("ul", { class: "refs timeline" }, arr(b.items).map(function (x) {
          return el("li", null, [el("span", { class: "yr", text: str(x[0]) }), el("div", null, rich(x[1]))]);
        }))];
        case "kv": return [el("table", { class: "kv" }, [el("tbody", null, arr(b.items).map(function (x) {
          return el("tr", null, [el("th", { text: x[0] }), el("td", null, rich(x[1]))]);
        }))])];
        case "mtoc": return [marginToc(b.items)];
        case "slot": return typeof SLOTS[b.name] === "function" ? [SLOTS[b.name](b)] : [];
        default: return [];
      }
    }
    // Long articles: a table of contents at the top of the margin (a folding list on phones).
    function marginToc(items) {
      var d = el("details", { class: "mtoc" }, [el("summary", { text: "本文目录" }), el("ol", null, arr(items).map(function (x) { return el("li", null, [part(x)]); }))]);
      var wide = window.matchMedia("(min-width: 761px)");
      d.open = wide.matches;
      return d;
    }
    arr(PG.body).forEach(function (b) {
      if (b.b === "sec") {
        box = el("section", { id: b.id || null });
        if (b.h) box.appendChild(heading("h2", { t: b.h, sn: b.sn }));
        art.appendChild(box);
        return;
      }
      render(b).forEach(function (n) { if (n) cur().appendChild(n); });
    });

    var S = PG.series || {};
    if (S.prev || S.next || S.up) {
      var nav = el("nav", { class: "series", "aria-label": "同系列" });
      nav.appendChild(el("div", { class: "prev" }, S.prev ? [el("small", { text: "上一篇" }), part(S.prev)] : []));
      nav.appendChild(el("div", { class: "up" }, S.up ? [part(S.up)] : []));
      nav.appendChild(el("div", { class: "next" }, S.next ? [el("small", { text: "下一篇" }), part(S.next)] : []));
      art.appendChild(nav);
    }
  })();
