  // ================= core: shared helpers, cross-links, math, navigation =================
  var DATA;
  try { DATA = JSON.parse(document.getElementById("data").textContent); } catch (e) { DATA = {}; }
  var SITE = DATA.site || {};
  var meta = DATA.meta || {};

  // ---------- DOM helpers: all text goes through textContent; external links are https-only ----------
  function safeUrl(u) { if (typeof u !== "string") return null; var s = u.trim(); return /^https:\/\/[^\s"'<>]+$/i.test(s) ? s : null; }
  function el(tag, attrs, kids) {
    var n = document.createElement(tag);
    if (attrs) for (var k in attrs) {
      if (!Object.prototype.hasOwnProperty.call(attrs, k)) continue;
      var v = attrs[k];
      if (v === null || v === undefined || v === false) continue;
      if (k === "class") n.className = v;
      else if (k === "text") n.textContent = String(v);
      else if (k === "href") { var u = safeUrl(v); if (u) { n.setAttribute("href", u); n.setAttribute("target", "_blank"); n.setAttribute("rel", "noopener noreferrer"); } }
      else if (k.slice(0, 2) === "on" && typeof v === "function") n.addEventListener(k.slice(2), v);
      else n.setAttribute(k, String(v));
    }
    (kids || []).forEach(function (c) { if (c === null || c === undefined || c === false) return; n.appendChild(typeof c === "string" ? document.createTextNode(c) : c); });
    return n;
  }
  var SVGNS = "http://www.w3.org/2000/svg";
  function sv(tag, attrs, kids) {
    var n = document.createElementNS(SVGNS, tag);
    if (attrs) for (var k in attrs) {
      if (!Object.prototype.hasOwnProperty.call(attrs, k)) continue;
      var v = attrs[k];
      if (v === null || v === undefined || v === false) continue;
      if (k === "text") n.textContent = String(v);
      else if (k.slice(0, 2) === "on" && typeof v === "function") n.addEventListener(k.slice(2), v);
      else n.setAttribute(k, String(v));
    }
    (kids || []).forEach(function (c) { if (c) n.appendChild(c); });
    return n;
  }
  function arr(x) { return Array.isArray(x) ? x : []; }
  function str(x) { return typeof x === "string" ? x : (x === null || x === undefined ? "" : String(x)); }

  // ---------- pages & cross-page links ----------
  var PAGES = arr(SITE.pages);
  var CUR_FILE = "";
  PAGES.forEach(function (p) { if (p.key === SITE.current) CUR_FILE = p.file; });
  function pageOf(id) {
    var sp = SITE.sectionPage || {};
    if (Object.prototype.hasOwnProperty.call(sp, id)) return sp[id];
    var pre = arr(SITE.prefixPage);
    for (var i = 0; i < pre.length; i++) if (id.indexOf(pre[i][0]) === 0) return pre[i][1];
    return null;
  }
  function hrefFor(id) { var f = pageOf(id); return (!f || f === CUR_FILE) ? "#" + id : f + "#" + id; }
  function align(id) {
    var t = document.getElementById(id);
    if (!t) return;
    var root = document.documentElement, prev = root.style.scrollBehavior;
    root.style.scrollBehavior = "auto";
    t.scrollIntoView({ block: "start" });
    root.style.scrollBehavior = prev;
  }
  function goTo(id, instant) {
    var t = document.getElementById(id);
    if (!t) {
      var f = pageOf(id);
      if (f && f !== CUR_FILE) window.location.href = f + "#" + id;
      return;
    }
    var p = t;
    while (p && p !== document.body) {
      if (typeof p._activate === "function") p._activate();
      if (p.tagName === "DETAILS") p.open = true;
      p = p.parentElement;
    }
    typeset(t);
    if (instant) align(id); else t.scrollIntoView({ block: "start" });
    t.classList.remove("flash"); void t.offsetWidth; t.classList.add("flash");
  }
  // Internal link: a real <a href> (works across pages, middle-click opens a tab); same-page clicks also open details and flash.
  function internalLink(targetId, cls, text, title) {
    var a = el("a", { class: cls, text: text, title: title || null });
    a.setAttribute("href", hrefFor(targetId));
    a.addEventListener("click", function (e) {
      if (e.button !== 0 || e.metaKey || e.ctrlKey || e.shiftKey || e.altKey) return;
      if (document.getElementById(targetId)) {
        e.preventDefault();
        try { window.history.pushState(null, "", "#" + targetId); } catch (err) { /* sandboxed frame */ }
        goTo(targetId);
      }
    });
    return a;
  }
  function refChip(targetId, label, ghost) { return internalLink(targetId, "cchip" + (ghost ? " ghost" : ""), label); }

  // Known concept / advanced-topic ids mentioned in prose become inline links.
  var XREF = DATA.xref || {};
  var conceptName = XREF.concepts || {}, advName = XREF.adv || {};
  var ID_RE = /(a-[a-z0-9]+(?:-[a-z0-9]+)*|[fgdrilnv]-[a-z0-9]+)/g;
  function rich(text) {
    var s = str(text), out = [], last = 0, m;
    ID_RE.lastIndex = 0;
    while ((m = ID_RE.exec(s)) !== null) {
      var id = m[1], prev = m.index > 0 ? s.charAt(m.index - 1) : "", next = s.charAt(m.index + id.length);
      var target = conceptName[id] ? "concept-" + id : (advName[id] ? "adv-" + id : null);
      if (!target || /[A-Za-z0-9_\-]/.test(prev) || /[A-Za-z0-9_]/.test(next)) continue;
      if (m.index > last) out.push(document.createTextNode(s.slice(last, m.index)));
      out.push(idLink(target, id, conceptName[id] || advName[id]));
      last = m.index + id.length;
    }
    if (last < s.length) out.push(document.createTextNode(s.slice(last)));
    return out;
  }
  function idLink(target, id, label) { return internalLink(target, "idref", id, label); }
  function paras(text) { return str(text).split(/\n\s*\n/).map(function (t) { return t.trim(); }).filter(Boolean).map(function (t) { return el("p", null, rich(t)); }); }
  function asideBox(label, text) { return str(text).trim() ? el("div", { class: "aside" }, [el("b", { text: label }), el("span", null, rich(text))]) : null; }
  function link(title, url) { return safeUrl(url) ? el("a", { href: url, text: title }) : el("span", { text: title }); }
  function ul(items, map) { return el("ul", { class: "plain" }, arr(items).map(function (x) { return el("li", null, [map ? map(x) : str(x)]); })); }
  function secHead(eyebrow, title, lede) { return el("div", { class: "sec-head" }, [el("div", { class: "eyebrow", text: eyebrow }), el("h2", { text: title }), lede ? el("p", { class: "lede", text: lede }) : null]); }
  function blk(title, kids) { return el("div", { class: "blk" }, [el("h4", { text: title })].concat(kids)); }
  function textBlk(title, text) { return str(text).trim() ? blk(title, [el("div", { class: "prose" }, paras(text))]) : null; }
  function fmtCit(n) { n = Number(n); if (!(n >= 0)) return "—"; if (n >= 1000) return (n / 1000).toFixed(n >= 10000 ? 0 : 1) + "k"; return String(n); }

  // ---------- math (MathJax, typeset lazily) ----------
  var mathReady = false, mathQueue = [];
  window.__atlasMathReady = function () { mathReady = true; var q = mathQueue.slice(); mathQueue = []; q.forEach(typeset); };
  function typeset(node) {
    if (!node) return;
    if (!mathReady || !window.MathJax || typeof window.MathJax.typesetPromise !== "function") { mathQueue.push(node); return; }
    try { window.MathJax.typesetPromise([node]).catch(function () { /* leave raw TeX visible */ }); } catch (e) { /* leave raw TeX visible */ }
  }
  function eqList(eqs) {
    eqs = arr(eqs).filter(function (q) { return q && str(q.tex).trim(); });
    if (!eqs.length) return null;
    return el("div", { class: "eqs" }, eqs.map(function (q) {
      return el("div", { class: "eq" }, [el("div", { class: "math-block", text: "\\[" + str(q.tex) + "\\]" }), q.explain_zh ? el("p", null, rich(q.explain_zh)) : null]);
    }));
  }
  document.addEventListener("toggle", function (e) { var t = e.target; if (t && t.tagName === "DETAILS" && t.open) typeset(t); }, true);

  // ---------- shared components ----------
  function makeTabs(views, storageKey) {
    var tabs = el("div", { class: "tabs", role: "tablist" });
    var holder = el("div");
    var panels = {};
    function show(id) {
      Array.prototype.forEach.call(tabs.children, function (b) { b.setAttribute("aria-selected", b.getAttribute("data-id") === id ? "true" : "false"); });
      views.forEach(function (v) { panels[v.id].hidden = v.id !== id; });
      typeset(panels[id]);
      if (storageKey) { try { localStorage.setItem(storageKey, id); } catch (e) { /* storage unavailable */ } }
    }
    views.forEach(function (v) {
      tabs.appendChild(el("button", { class: "tab", role: "tab", type: "button", "data-id": v.id, text: v.label, onclick: function () { show(v.id); } }));
      var p = el("div", { role: "tabpanel" }, [v.node()]);
      p._activate = function () { show(v.id); };
      panels[v.id] = p; holder.appendChild(p);
    });
    var initial = views[0].id;
    if (storageKey) { try { var s = localStorage.getItem(storageKey); if (s && panels[s]) initial = s; } catch (e) { /* storage unavailable */ } }
    show(initial);
    return el("div", null, [tabs, holder]);
  }
  function cChip(id, ghost) { return conceptName[id] ? refChip("concept-" + id, conceptName[id], ghost) : null; }
  function aChip(id) { return advName[id] ? refChip("adv-" + id, advName[id], true) : null; }
  function chipRow(label, nodes) { nodes = nodes.filter(Boolean); return nodes.length ? el("div", { class: "chips" }, [el("span", { class: "lbl", text: label })].concat(nodes)) : null; }
  function resList(items) {
    var ty = { book: "教材", course: "课程", paper: "论文", tutorial: "教程", code: "代码", video: "视频", blog: "文章" };
    return el("div", { class: "res" }, arr(items).map(function (r) { return el("div", null, [el("span", { class: "ty", text: ty[r.type] || r.type || "" }), el("span", null, [link(r.title, r.url), r.note_zh ? el("small", { text: r.note_zh }) : null])]); }));
  }
  function qaList(items, qk, ak) { return el("div", null, arr(items).map(function (q) { return el("details", { class: "qa" }, [el("summary", { text: q[qk] }), el("p", null, rich(q[ak]))]); })); }
  var anchorShort = { quark: "Quark", ha: "Ha et al." };
  function walkId(anchor, sid) { return "walk-" + anchor + "-" + sid; }

  // ---------- page frame: sections, site nav, in-page toc, breadcrumbs, pager ----------
  var main = document.getElementById("main");
  var navEl = document.getElementById("site-nav");
  var tocItems = [];
  function addSection(id, tocLabel, nodes) {
    var s = el("section", { id: id }, nodes);
    main.appendChild(s);
    if (tocLabel) tocItems.push({ id: id, label: tocLabel });
    return s;
  }
  function addTocItem(id, label) { tocItems.push({ id: id, label: label }); }
  function pageLink(p, cls) { var a = el("a", { class: cls, text: p.label }); a.setAttribute("href", p.href || p.file); return a; }
  function finishPage() {
    var real = PAGES.filter(function (p) { return !p.alias; });
    var cur = null, curIdx = -1;
    real.forEach(function (p, i) { if (p.key === SITE.current) { cur = p; curIdx = i; } });

    // Sidebar (desktop) / top bar (mobile): all pages grouped, current page expanded with its own sections.
    var brand = el("a", { class: "brand", text: SITE.brand || "3D 临场研究图谱" }); brand.setAttribute("href", "index.html");
    var ol = el("ol");
    var lastGroup = null, subLinks = {}, curLink = null;
    PAGES.forEach(function (p) {
      if (p.group && p.group !== lastGroup) { ol.appendChild(el("li", { class: "grp", text: p.group })); }
      lastGroup = p.group || lastGroup;
      var isCur = !p.alias && p.key === SITE.current;
      var a = pageLink(p, "page" + (isCur ? " cur" : ""));
      if (isCur) { a.setAttribute("aria-current", "page"); curLink = a; }
      var li = el("li", null, [a]);
      if (isCur && tocItems.length > 1) {
        li.appendChild(el("ol", { class: "sub" }, tocItems.map(function (t) {
          var s = internalLink(t.id, "", t.label); s.setAttribute("data-id", t.id); subLinks[t.id] = s;
          return el("li", null, [s]);
        })));
      }
      ol.appendChild(li);
    });
    navEl.appendChild(brand);
    navEl.appendChild(el("div", { class: "ramp", "aria-hidden": "true" }));
    navEl.appendChild(ol);

    // Top of main: breadcrumbs + (mobile only) this page's sections.
    var head = el("div", { class: "page-head" });
    if (cur && cur.key !== "home") {
      var home = el("a", { text: SITE.brand || "3D 临场研究图谱" }); home.setAttribute("href", "index.html");
      var groupPages = real.filter(function (p) { return p.group === cur.group; });
      head.appendChild(el("div", { class: "crumbs" }, [home, el("span", { class: "sep", text: "›" }), el("span", { text: cur.group || "" }), el("span", { class: "sep", text: "›" }), el("b", { text: cur.label }), el("span", { class: "mono", text: "（" + (groupPages.indexOf(cur) + 1) + " / " + groupPages.length + "）" })]));
    }
    if (tocItems.length > 1) head.appendChild(el("nav", { class: "toc-mobile", "aria-label": "本页目录" }, [el("div", { class: "chips" }, [el("span", { class: "lbl", text: "本页" })].concat(tocItems.map(function (t) { return internalLink(t.id, "cchip ghost", t.label); })))]));
    if (!head.querySelector(".crumbs")) head.classList.add("only-mobile");
    if (head.childNodes.length) main.insertBefore(head, main.firstChild);

    // Bottom of main: previous / next page.
    if (curIdx >= 0) {
      var prev = real[curIdx - 1], next = real[curIdx + 1];
      var pager = el("nav", { class: "pager", "aria-label": "翻页" });
      if (prev) { var pa = el("a", { class: "prev" }, [el("small", { text: "← 上一页" + (prev.group ? " · " + prev.group : "") }), el("b", { text: prev.label })]); pa.setAttribute("href", prev.file); pager.appendChild(pa); }
      if (next) { var na = el("a", { class: "next" }, [el("small", { text: "下一页" + (next.group ? " · " + next.group : "") + " →" }), el("b", { text: next.label })]); na.setAttribute("href", next.file); pager.appendChild(na); }
      main.appendChild(pager);
    }

    // Keep the current page visible in the horizontal (mobile) bar.
    if (curLink && navEl.scrollWidth > navEl.clientWidth) navEl.scrollLeft = Math.max(0, curLink.offsetLeft - navEl.clientWidth / 3);

    // Highlight the section being read: the last TOC target whose top has passed 25% of the viewport.
    if (Object.keys(subLinks).length) {
      var ticking = false;
      var highlight = function () {
        ticking = false;
        var line = window.innerHeight * 0.25, active = tocItems[0] ? tocItems[0].id : null;
        tocItems.forEach(function (t) {
          var n = document.getElementById(t.id);
          if (n && n.offsetParent !== null && n.getBoundingClientRect().top <= line) active = t.id;
        });
        for (var k in subLinks) subLinks[k].classList.toggle("on", k === active);
      };
      window.addEventListener("scroll", function () { if (!ticking) { ticking = true; window.requestAnimationFrame(highlight); } }, { passive: true });
      window.addEventListener("resize", highlight);
      highlight();
    }
    var h = window.location.hash ? window.location.hash.slice(1) : "";
    if (h && /^[A-Za-z0-9._~-]+$/.test(h)) {
      var userMoved = false;
      var stop = function () { userMoved = true; };
      ["wheel", "touchstart", "keydown", "mousedown"].forEach(function (ev) { window.addEventListener(ev, stop, { once: true, passive: true }); });
      var settle = function () { if (!userMoved) align(h); };
      goTo(h, true);
      if (document.fonts && document.fonts.ready) document.fonts.ready.then(function () { window.requestAnimationFrame(settle); });
      window.addEventListener("load", function () { window.requestAnimationFrame(settle); });
      [400, 1200, 2500].forEach(function (ms) { setTimeout(settle, ms); });
    }
  }
