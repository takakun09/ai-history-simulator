import { api, esc } from "/assets/app.js";

const LEVEL_TEXT = (l) => `${l.min}–${l.max > 3 ? 3 : l.max} 分`;

function guideHtml(guide) {
  return `
    <div class="level-strip">
      ${guide.levels.map((l) => `<span class="lv lv-${l.key}">${esc(l.label)} <small>${LEVEL_TEXT(l)}</small></span>`).join("")}
    </div>
    <div class="guard-grid">
      ${guide.dimensions.map((d) => `
        <div class="gcard">
          <b>${esc(d.name)}</b>
          <p>${esc(d.meaning)}</p>
          <div class="gl"><span class="tag low">低</span>${esc(d.low)}</div>
          <div class="gl"><span class="tag high">高</span>${esc(d.high)}</div>
        </div>`).join("")}
    </div>`;
}

async function load() {
  const [d, guide] = await Promise.all([api("/api/analytics"), api("/api/rubric")]);
  const p = d.profile || { count: 0, per_dimension: {} };

  document.getElementById("stats").innerHTML = `
    <div class="stat"><b>${d.counts.decisions}</b><span>抉择提交</span></div>
    <div class="stat"><b>${d.counts.checks}</b><span>史料核对</span></div>
    <div class="stat"><b>${d.counts.figures}</b><span>历史人物</span></div>
    <div class="stat"><b>${p.count ? esc(p.per_dimension[p.weakest]?.name || "—") : "—"}</b><span>最弱维度</span></div>
    <div class="stat"><b>${(d.hint_usage && d.hint_usage.n) ? d.hint_usage.avg : "—"}</b><span>平均提示级数（${(d.hint_usage && d.hint_usage.n) ? d.hint_usage.used_share + "% 用过提示" : "无数据"}）</span></div>
    <div class="stat"><b>${typeof d.self_gap === "number" ? (d.self_gap > 0 ? "+" : "") + d.self_gap.toFixed(1) : "—"}</b><span>自评偏差（正=高估）</span></div>`;

  const dims = document.getElementById("dims");
  if (!p.count) {
    dims.innerHTML = '<div class="empty">还没有学生提交。</div>';
  } else {
    dims.innerHTML = guide.dimensions.map((dim) => {
      const v = p.per_dimension[dim.key] || { pct: 0, avg: "—", max: 3 };
      const chip = v.level ? `<span class="lv lv-${v.level_key}">${esc(v.level)}</span>` : "";
      return `<div class="dim-row"><div>${esc(dim.name)}</div>
        <div class="dim-bar"><i style="width:${v.pct}%"></i></div>
        <div class="dim-val">${v.avg} / ${v.max} ${chip}</div></div>`;
    }).join("")
      + (p.weakest
        ? `<div class="fb warn" style="margin-top:12px">全体最需要加强：<b>${esc(p.per_dimension[p.weakest].name)}</b></div>`
        : "");
  }

  document.getElementById("guide").innerHTML = guideHtml(guide);

  const recent = document.getElementById("recent");
  const rows = d.recent || [];
  recent.innerHTML = rows.length ? rows.map((r) => {
    const res = r.result || {};
    const tags = [];
    if (r.kind === "check") tags.push('<span class="pill">史料核对</span>');
    if (r.hints_used) tags.push(`<span class="pill">用了 ${r.hints_used} 级提示</span>`);
    return `<div class="rec">
      <div class="rec-head"><b>${esc(r.figure || "")}</b> · ${esc(r.dilemma || "")}
        <span class="rec-score">${res.total ?? "—"} / ${res.max_total ?? "—"}</span></div>
      <div class="rec-body">选择：${esc(r.choice || "")}</div>
      <div class="rec-arg">${esc((r.argument || "").slice(0, 120))}${(r.argument || "").length > 120 ? "…" : ""}</div>
      <div class="rec-time">${esc(r.created_at || "")}${r.student_id ? " · " + esc(r.student_id) : ""} ${tags.join(" ")}</div>
    </div>`;
  }).join("") : '<div class="empty">暂无记录。</div>';
}

load().catch((e) => {
  document.getElementById("stats").innerHTML = `<div class="empty">加载失败：${esc(e.message)}</div>`;
});
