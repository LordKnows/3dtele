  // ================= lib: DOM, text and math helpers shared by every page =================
  // A page script defines rich(text) (inline cross-links); paras() and eqList() call it.
  var DATA;
  try { DATA = JSON.parse(document.getElementById("data").textContent); } catch (e) { DATA = {}; }
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
  function paras(text) { return str(text).split(/\n\s*\n/).map(function (t) { return t.trim(); }).filter(Boolean).map(function (t) { return el("p", null, rich(t)); }); }
  function link(title, url) { return safeUrl(url) ? el("a", { href: url, text: title }) : el("span", { text: title }); }
  function ul(items, map) { return el("ul", { class: "plain" }, arr(items).map(function (x) { return el("li", null, [map ? map(x) : str(x)]); })); }
  function fmtCit(n) { n = Number(n); if (!(n >= 0)) return "—"; if (n >= 1000) return (n / 1000).toFixed(n >= 10000 ? 0 : 1) + "k"; return String(n); }

  // ---------- math (MathJax, typeset lazily) ----------
  var mathReady = false, mathQueue = [];
  function mathUsable() { return !!(window.MathJax && typeof window.MathJax.typesetPromise === "function"); }
  function flushMath() { mathReady = true; var q = mathQueue.slice(); mathQueue = []; q.forEach(typeset); }
  window.__atlasMathReady = flushMath;
  // MathJax may finish loading before this script runs (cached/async), so also poll for it.
  var mathPoll = setInterval(function () { if (mathUsable()) { clearInterval(mathPoll); flushMath(); } }, 200);
  setTimeout(function () { clearInterval(mathPoll); }, 30000);
  function typeset(node) {
    if (!node) return;
    if (!mathReady && mathUsable()) mathReady = true;
    if (!mathReady || !mathUsable()) { mathQueue.push(node); return; }
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
