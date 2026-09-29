  // ================= page: 研究机会 =================
  var ideas = arr(DATA.ideas);
  if (ideas.length) {
    var decLabel = { pursue: "建议推进", pursue_with_repositioning: "重新定位后推进", drop: "建议放弃" };
    var verLabel = { open: "查新：空白", partially_scooped: "查新：部分已被做", scooped: "查新：已被做" };
    function scoreRow(label, v) { var n = Math.max(0, Math.min(10, Number(v) || 0)); return el("div", { class: "score" }, [el("span", { class: "num", text: label + " " + n }), el("span", { class: "track" }, [el("i", { style: "width:" + (n * 10) + "%" })])]); }
    addSection("ideas", "研究机会", [
      secHead("Research opportunities", "研究机会：经对抗查新与评审的方向", meta.ideas_lede || ""),
      el("div", { style: "display:grid;gap:12px" }, ideas.map(function (it, i) {
        var s = it.scores || {}; var sh = it.sharpened || {}; var ex = it.experiments || {}; var nov = it.novelty || {}; var ef = it.effort || {};
        return el("details", { class: "idea", id: "idea-" + it.id }, [
          el("summary", null, [
            el("span", { class: "rank", text: String(i + 1).padStart(2, "0") }),
            el("div", { class: "head" }, [el("h3", { text: sh.title_zh || sh.title || it.name }), sh.title_en ? el("span", { class: "en-title", text: sh.title_en }) : null, el("p", { text: sh.one_liner || "" }), el("div", { class: "pills" }, [el("span", { class: "pill " + it.decision, text: decLabel[it.decision] || it.decision }), el("span", { class: "pill " + nov.verdict, text: verLabel[nov.verdict] || nov.verdict }), it.venue ? el("span", { class: "chip", text: it.venue }) : null])]),
            el("div", { class: "ov" }, [String(s.overall != null ? s.overall : "–"), el("small", { text: "综合分" })])
          ]),
          el("div", { class: "idea-body" }, [
            el("div", { class: "scores" }, [scoreRow("新颖", s.novelty), scoreRow("意义", s.significance), scoreRow("可行", s.feasibility), scoreRow("临场契合", s.telepresence_fit)]),
            el("div", { class: "idea-grid" }, [
              el("div", { class: "blk" }, [el("h4", { text: "核心论点（可证伪）" }), el("p", { text: sh.core_claim })]),
              el("div", { class: "blk" }, [el("h4", { text: "关键洞察" }), el("p", { text: sh.key_insight })]),
              el("div", { class: "blk" }, [el("h4", { text: "方法" }), el("p", { text: sh.method })]),
              el("div", { class: "blk" }, [el("h4", { text: "为什么不是工程改进" }), el("p", { text: sh.why_not_engineering })]),
              el("div", { class: "blk" }, [el("h4", { text: "与已有工作的区分" }), el("p", { text: sh.differentiation })]),
              el("div", { class: "blk" }, [el("h4", { text: "查新后剩余的可辩护新意" }), el("p", { text: nov.remaining_novel_angle })])
            ]),
            arr(nov.threats).length ? el("div", { class: "blk" }, [el("h4", { text: "主要撞车风险（查新找到的相近工作）" }), el("div", { style: "display:grid;gap:8px" }, arr(nov.threats).map(function (t) { return el("div", { class: "threat " + t.overlap }, [el("span", null, [link(t.title, t.url), " · " + (t.year || "") + (t.venue ? " · " + t.venue : "") + " · 重叠度 " + ({ high: "高", medium: "中", low: "低" }[t.overlap] || t.overlap)]), el("span", { text: "重叠：" + (t.what_overlaps || "") }), el("span", { text: "差异：" + (t.what_remains_different || "") })]); }))]) : null,
            el("div", { class: "idea-grid" }, [
              el("div", { class: "blk" }, [el("h4", { text: "数据集" }), ul(ex.datasets)]),
              el("div", { class: "blk" }, [el("h4", { text: "对比基线" }), ul(ex.baselines)]),
              el("div", { class: "blk" }, [el("h4", { text: "指标" }), ul(ex.metrics)]),
              el("div", { class: "blk" }, [el("h4", { text: "关键消融" }), ul(ex.key_ablations)])
            ]),
            ex.capture_notes ? el("div", { class: "blk" }, [el("h4", { text: ex.needs_custom_capture ? "需要自建采集" : "采集说明" }), el("p", { text: ex.capture_notes })]) : null,
            el("div", { class: "idea-grid" }, [
              el("div", { class: "blk" }, [el("h4", { text: "两周内的验证实验" }), el("p", { text: it.first_two_week_test })]),
              el("div", { class: "blk" }, [el("h4", { text: "止损标准" }), el("p", { text: it.kill_criteria })])
            ]),
            arr(it.reviewer_objections).length ? el("div", { class: "blk" }, [el("h4", { text: "审稿人可能的质疑与回应" }), el("div", { style: "display:grid;gap:10px" }, arr(it.reviewer_objections).map(function (o) { return el("div", { class: "obj" }, [el("b", { text: "质疑：" + o.objection }), el("span", { text: "回应：" + o.rebuttal })]); }))]) : null,
            el("div", { class: "kv" }, [
              el("div", null, [el("span", { class: "k", text: "周期" }), el("span", { class: "v", text: ef.months || "" })]),
              el("div", null, [el("span", { class: "k", text: "人力" }), el("span", { class: "v", text: ef.people || "" })]),
              el("div", null, [el("span", { class: "k", text: "算力" }), el("span", { class: "v", text: ef.compute || "" })]),
              el("div", null, [el("span", { class: "k", text: "目标会议" }), el("span", { class: "v", text: it.venue || "" })])
            ]),
            it.synergies ? el("div", { class: "blk" }, [el("h4", { text: "可组合的方向" }), el("p", { text: it.synergies })]) : null
          ])
        ]);
      }))
    ]);
  }
