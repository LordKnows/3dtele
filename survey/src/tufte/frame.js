  // ================= frame (Tufte site): links, notes, hover previews, top bar, theme =================
  var SITE = DATA.site || {};
  var ROOT = str(SITE.root);
  var XREF = DATA.xref || {};
  function hasX(key) { return Object.prototype.hasOwnProperty.call(XREF, key); }

  // ---------- internal links: urls are relative to the site root; pages sit at different depths ----------
  var SAFE_PATH = /^[A-Za-z0-9][A-Za-z0-9._\/-]*(#[A-Za-z0-9._-]+)?$/;
  function relHref(u) {
    u = str(u);
    if (!SAFE_PATH.test(u)) return null;
    var cut = u.indexOf("#"), path = cut < 0 ? u : u.slice(0, cut);
    if (path === SITE.path) return cut < 0 ? "#" : u.slice(cut);
    return ROOT + u;
  }
  function pageLink(u, text, cls) {
    var h = relHref(u);
    if (!h) return el("span", { class: cls || null, text: text });
    var a = el("a", { class: cls || null, text: text });
    a.setAttribute("href", h);
    return a;
  }
  // A link to a known entry (concept, topic, paper, step...). data-xref drives the hover preview.
  function xlink(key, text, cls) {
    if (!hasX(key)) return text ? document.createTextNode(text) : null;
    var x = XREF[key], a = pageLink(x.u, text || x.n || x.t, cls);
    a.setAttribute("data-xref", key);
    return a;
  }

  // Concept / topic ids mentioned in prose ("见 g-pinhole") become links labelled with the entry's short name.
  var ID_RE = /(a-[a-z0-9]+(?:-[a-z0-9]+)*|[fgdrilnv]-[a-z0-9]+)/g;
  var CJK = /[　-〿㐀-鿿＀-￯]/;
  function rich(text) {
    var s = str(text), out = [], last = 0, m;
    ID_RE.lastIndex = 0;
    while ((m = ID_RE.exec(s)) !== null) {
      var id = m[1], prev = m.index > 0 ? s.charAt(m.index - 1) : "", next = s.charAt(m.index + id.length);
      var key = hasX("concept-" + id) ? "concept-" + id : (hasX("adv-" + id) ? "adv-" + id : null);
      if (!key || /[A-Za-z0-9_\-]/.test(prev) || /[A-Za-z0-9_]/.test(next)) continue;
      // The prose spaces ids off from Chinese text; a Chinese label needs no such space.
      var before = s.slice(last, m.index);
      if (/ $/.test(before) && CJK.test(before.charAt(before.length - 2))) before = before.slice(0, -1);
      if (before) out.push(document.createTextNode(before));
      out.push(xlink(key, null, "xref"));
      last = m.index + id.length;
      if (s.charAt(last) === " " && CJK.test(s.charAt(last + 1))) last++;
    }
    if (last < s.length) out.push(document.createTextNode(s.slice(last)));
    return out;
  }
  function lines(text) { return str(text).split(/\n+/).map(function (t) { return t.trim(); }).filter(Boolean).map(function (t) { return el("p", null, rich(t)); }); }

  // ---------- side notes (numbered) and margin notes (unnumbered); on phones they fold behind a toggle ----------
  var noteSeq = 0;
  function sidenote(kids) {
    var id = "sn-" + (++noteSeq);
    return el("span", { class: "note-wrap" }, [
      el("label", { for: id, class: "margin-toggle sidenote-number", "aria-label": "旁注" }),
      el("input", { type: "checkbox", id: id, class: "margin-toggle" }),
      el("span", { class: "sidenote" }, kids)
    ]);
  }
  function marginnote(kids) {
    var id = "mn-" + (++noteSeq);
    return el("span", { class: "note-wrap" }, [
      el("label", { for: id, class: "margin-toggle", "aria-label": "边注", text: "⊕" }),
      el("input", { type: "checkbox", id: id, class: "margin-toggle" }),
      el("span", { class: "marginnote" }, kids)
    ]);
  }
  function noteLabel(text) { return el("span", { class: "note-label", text: text }); }

  // ---------- article scaffolding ----------
  var main = document.getElementById("main");
  var art = main.querySelector("article");
  function section(id, title, kids) {
    var s = el("section", { id: id }, [title ? el("h2", { text: title }) : null].concat(kids));
    art.appendChild(s);
    return s;
  }
  function articleHead(o) {
    var crumbs = el("nav", { class: "crumbs", "aria-label": "位置" });
    arr(SITE.crumbs).forEach(function (c, i) {
      if (i) crumbs.appendChild(el("span", { class: "sep", text: "›", "aria-hidden": "true" }));
      crumbs.appendChild(c[1] ? pageLink(c[1], c[0]) : el("span", { text: c[0] }));
    });
    art.appendChild(el("header", { class: "art-head" }, [
      crumbs,
      el("h1", { text: o.title }),
      o.subtitle ? el("p", { class: "subtitle", text: o.subtitle }) : null,
      o.meta ? el("p", { class: "meta" }, o.meta) : null
    ]));
    if (o.epigraph) art.appendChild(el("div", { class: "epigraph" }, [el("blockquote", null, [el("p", null, rich(o.epigraph))])]));
  }
  // Previous / next in the series, each with its hover preview.
  function seriesNav(prevKey, nextKey, indexUrl, indexLabel) {
    var nav = el("nav", { class: "series", "aria-label": "同系列" });
    nav.appendChild(el("div", { class: "prev" }, prevKey && hasX(prevKey) ? [el("small", { text: "上一篇" }), xlink(prevKey)] : []));
    nav.appendChild(el("div", { class: "up" }, indexUrl ? [pageLink(indexUrl, indexLabel)] : []));
    nav.appendChild(el("div", { class: "next" }, nextKey && hasX(nextKey) ? [el("small", { text: "下一篇" }), xlink(nextKey)] : []));
    art.appendChild(nav);
  }

  // ---------- hover preview for internal links: mouse (after 300 ms) or keyboard focus; never on touch ----------
  var tip = null, tipTimer = 0, tipFor = null;
  function hideTip() {
    clearTimeout(tipTimer);
    if (tip) tip.hidden = true;
    if (tipFor) { tipFor.removeAttribute("aria-describedby"); tipFor = null; }
  }
  function showTip(a) {
    var key = a.getAttribute("data-xref");
    if (!hasX(key)) return;
    var x = XREF[key];
    if (!tip) { tip = el("div", { class: "xtip", id: "xtip", role: "tooltip" }); document.body.appendChild(tip); }
    tip.textContent = "";
    if (x.m) tip.appendChild(el("div", { class: "xt-m", text: x.m }));
    tip.appendChild(el("div", { class: "xt-t", text: x.t }));
    if (x.e) tip.appendChild(el("div", { class: "xt-e", text: x.e }));
    if (x.s) tip.appendChild(el("p", { class: "xt-s", text: x.s }));
    tip.hidden = false;
    var r = a.getClientRects()[0] || a.getBoundingClientRect(), vw = document.documentElement.clientWidth;
    var w = tip.offsetWidth, h = tip.offsetHeight;
    var left = Math.max(8, Math.min(r.left, vw - w - 8));
    var top = r.bottom + 6;
    if (top + h > window.innerHeight - 8 && r.top - h - 6 > 8) top = r.top - h - 6;
    tip.style.left = Math.round(left + window.pageXOffset) + "px";
    tip.style.top = Math.round(top + window.pageYOffset) + "px";
    a.setAttribute("aria-describedby", "xtip");
    tipFor = a;
  }
  function xrefTarget(e) { return e.target && e.target.closest ? e.target.closest("a[data-xref]") : null; }
  document.addEventListener("pointerover", function (e) {
    var a = xrefTarget(e);
    if (!a || e.pointerType !== "mouse" || a === tipFor) return;
    clearTimeout(tipTimer);
    tipTimer = setTimeout(function () { showTip(a); }, 300);
  });
  document.addEventListener("pointerout", function (e) {
    var a = xrefTarget(e);
    if (!a || (e.relatedTarget && a.contains(e.relatedTarget))) return;
    hideTip();
  });
  document.addEventListener("focusin", function (e) {
    var a = xrefTarget(e);
    if (a && a.matches(":focus-visible")) showTip(a);
  });
  document.addEventListener("focusout", function (e) { if (xrefTarget(e)) hideTip(); });
  document.addEventListener("keydown", function (e) { if (e.key === "Escape") hideTip(); });
  window.addEventListener("scroll", function () { if (tipFor && !tipFor.matches(":focus-visible")) hideTip(); }, { passive: true });

  // ---------- top bar: four menus with dropdowns (hover or click on desktop, a folding list on phones) ----------
  var wide = window.matchMedia("(min-width: 761px)");
  function setOpen(li, open) {
    var btn = li.querySelector(".menu-btn");
    if (open) Array.prototype.forEach.call(li.parentNode.children, function (o) { if (o !== li) setOpen(o, false); });
    li.classList.toggle("open", open);
    btn.setAttribute("aria-expanded", open ? "true" : "false");
    if (!open) li._hover = false;
  }
  function buildTopbar() {
    var bar = document.getElementById("topbar");
    var menus = el("ul", { class: "menus", id: "menus" });
    arr(SITE.nav).forEach(function (m) {
      var id = "menu-" + m.key;
      var btn = el("button", { type: "button", class: "menu-btn", "aria-expanded": "false", "aria-controls": id, text: m.label });
      var list = el("ul", { class: "drop", id: id }, arr(m.items).map(function (it) {
        var a = pageLink(it[1], it[0]);
        if (it[1] === SITE.navItem) a.classList.add("cur");
        if (it[1] === SITE.path) a.setAttribute("aria-current", "page");
        return el("li", null, [a]);
      }));
      var li = el("li", { class: "menu" + (m.key === SITE.navCur ? " cur" : "") }, [btn, list]);
      btn.addEventListener("click", function () {
        // A click on a menu the mouse already opened keeps it open instead of closing it again.
        if (li._hover) { li._hover = false; return; }
        setOpen(li, !li.classList.contains("open"));
      });
      btn.addEventListener("keydown", function (e) {
        if (e.key === "ArrowDown") { e.preventDefault(); setOpen(li, true); var f = list.querySelector("a"); if (f) f.focus(); }
      });
      li.addEventListener("pointerenter", function (e) { if (e.pointerType === "mouse" && wide.matches) { setOpen(li, true); li._hover = true; } });
      li.addEventListener("pointerleave", function (e) { if (e.pointerType === "mouse" && wide.matches) setOpen(li, false); });
      li.addEventListener("focusout", function (e) { if (wide.matches && !li.contains(e.relatedTarget)) setOpen(li, false); });
      li.addEventListener("keydown", function (e) { if (e.key === "Escape" && li.classList.contains("open")) { setOpen(li, false); btn.focus(); } });
      menus.appendChild(li);
    });
    var burger = el("button", { type: "button", class: "burger", "aria-expanded": "false", "aria-controls": "menus", text: "Menu" });
    burger.addEventListener("click", function () {
      var open = !bar.classList.contains("nav-open");
      bar.classList.toggle("nav-open", open);
      burger.setAttribute("aria-expanded", open ? "true" : "false");
    });
    var themeBtn = el("button", { type: "button", class: "theme-btn" });
    function darkNow() {
      var t = document.documentElement.getAttribute("data-theme");
      return t ? t === "dark" : window.matchMedia("(prefers-color-scheme: dark)").matches;
    }
    function paintThemeBtn() {
      var dark = darkNow();
      themeBtn.textContent = dark ? "Light" : "Dark";
      themeBtn.setAttribute("aria-label", dark ? "切换到浅色" : "切换到深色");
    }
    themeBtn.addEventListener("click", function () {
      var next = darkNow() ? "light" : "dark";
      var system = window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light";
      // Choosing what the system already shows drops the override, so the page follows the system again.
      if (next === system) document.documentElement.removeAttribute("data-theme");
      else document.documentElement.setAttribute("data-theme", next);
      try { if (next === system) localStorage.removeItem("atlas-theme"); else localStorage.setItem("atlas-theme", next); } catch (e) { /* storage unavailable */ }
      paintThemeBtn();
    });
    window.matchMedia("(prefers-color-scheme: dark)").addEventListener("change", paintThemeBtn);
    paintThemeBtn();
    bar.appendChild(el("div", { class: "bar-in" }, [pageLink("index.html", SITE.brand || "", "brand"), el("nav", { class: "site-nav", "aria-label": "站点导航" }, [menus]), themeBtn, burger]));
    document.addEventListener("click", function (e) {
      if (!bar.contains(e.target)) Array.prototype.forEach.call(menus.children, function (li) { setOpen(li, false); });
    });
  }

  function finishPage() {
    buildTopbar();
    var foot = document.getElementById("site-foot");
    if (foot) foot.appendChild(el("p", null, [pageLink("index.html", SITE.brand || ""), SITE.date ? " · 内容截至 " + SITE.date : ""]));
    typeset(main);
    // Deep links (#id): the page is rendered by script, so jump once it exists and again after fonts settle.
    var h = window.location.hash ? window.location.hash.slice(1) : "";
    if (h && /^[A-Za-z0-9._~-]+$/.test(h) && document.getElementById(h)) {
      var moved = false;
      ["wheel", "touchstart", "keydown", "mousedown"].forEach(function (ev) { window.addEventListener(ev, function () { moved = true; }, { once: true, passive: true }); });
      var settle = function () { var t = document.getElementById(h); if (t && !moved) t.scrollIntoView({ block: "start" }); };
      settle();
      if (document.fonts && document.fonts.ready) document.fonts.ready.then(function () { window.requestAnimationFrame(settle); });
      [400, 1200, 2500].forEach(function (ms) { setTimeout(settle, ms); });
    }
  }
