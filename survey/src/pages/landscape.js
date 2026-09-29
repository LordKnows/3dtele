  // ================= page: 领域全景 + 范式对比 + 趋势与挑战 =================
  var synth = DATA.synth || {};
  if (arr(synth.field_map).length) {
    addSection("map", "领域全景", [
      secHead("Field map", "端到端技术栈全景", "从采集到显示与交互，每一层的最新水平、成熟度（1 = 研究原型，5 = 已产品化）与当前瓶颈。"),
      el("div", { class: "stack" }, arr(synth.field_map).map(function (Lr) {
        var m = Math.max(0, Math.min(5, Math.round(Number(Lr.maturity) || 0)));
        var bar = el("div", { class: "bar", "aria-label": "成熟度 " + m + " / 5" });
        for (var i = 1; i <= 5; i++) bar.appendChild(el("i", { class: i <= m ? "f" + i : "" }));
        return el("div", { class: "layer" }, [
          el("div", { class: "name" }, [el("b", { text: Lr.layer_zh }), el("span", { text: Lr.layer_en })]),
          el("div", { class: "body" }, [el("div", { class: "chips" }, arr(Lr.components_zh).map(function (c) { return el("span", { class: "chip", text: c }); })), el("p", { text: Lr.state_of_art_zh }), el("p", { class: "bneck" }, [el("em", { text: "瓶颈 " }), Lr.bottleneck_zh || ""])]),
          el("div", { class: "mat" }, [el("small", { text: "成熟度 " + m + " / 5" }), bar])
        ]);
      }))
    ]);
  }
  if (arr(synth.paradigms).length) {
    addSection("paradigms", "范式对比", [
      secHead("Paradigms", "表示与渲染范式对比"),
      el("div", { class: "tbl-wrap" }, [el("table", null, [
        el("thead", null, [el("tr", null, ["范式", "核心思路", "优势", "劣势", "代表工作", "展望"].map(function (h) { return el("th", { text: h }); }))]),
        el("tbody", null, arr(synth.paradigms).map(function (p) { return el("tr", null, [el("td", { class: "dim", text: p.name }), el("td", { text: p.idea_zh }), el("td", { text: p.strengths_zh }), el("td", { text: p.weaknesses_zh }), el("td", { text: arr(p.exemplars).join("；") }), el("td", { text: p.outlook_zh })]); }))
      ])])
    ]);
  }

  if (arr(synth.trends_zh).length || arr(synth.grand_challenges_zh).length) {
    addSection("trends", "趋势与挑战", [
      secHead("Trends & challenges", "跨方向趋势与重大挑战"),
      arr(synth.trends_zh).length ? el("div", { class: "cards" }, arr(synth.trends_zh).map(function (t) { return el("div", { class: "card" }, [el("h4", { text: t.trend }), el("span", { class: "lbl", text: "证据" }), el("p", { text: t.evidence }), el("span", { class: "lbl", text: "含义" }), el("p", { text: t.implication })]); })) : null,
      arr(synth.grand_challenges_zh).length ? el("h3", { class: "sub", text: "重大挑战" }) : null,
      arr(synth.grand_challenges_zh).length ? el("div", { class: "cards" }, arr(synth.grand_challenges_zh).map(function (g) { return el("div", { class: "card" }, [el("h4", { text: g.title }), el("p", { text: g.description }), el("span", { class: "lbl", text: "为什么难" }), el("p", { text: g.why_hard }), el("span", { class: "lbl", text: "有希望的方向" }), el("p", { text: g.promising_directions })]); })) : null,
      arr(synth.predictions_zh).length ? el("div", { class: "blk" }, [el("h3", { class: "sub", text: "未来 1–3 年判断" }), ul(synth.predictions_zh)]) : null
    ]);
  }
