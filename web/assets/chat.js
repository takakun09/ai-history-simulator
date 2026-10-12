import { api, qs, esc, store } from "/assets/app.js";

const $ = (id) => document.getElementById(id);
const figId = qs("figure");
let figure = null;
let messages = [];
let cfg = store.get("hs_api", { provider: "mock", model: "", base_url: "", api_key: "" });

function studentId() {
  let id = localStorage.getItem("hs_student");
  if (!id) { id = "s-" + Math.random().toString(36).slice(2, 10); localStorage.setItem("hs_student", id); }
  return id;
}
const STUDENT = studentId();

const QUICK_ASKS = ["你的依据是什么？", "还有别的说法吗？", "当时的人会怎么看？", "你确定吗？"];

async function boot() {
  if (!figId) { location.href = "/"; return; }
  try { figure = await api(`/api/figures/${encodeURIComponent(figId)}`); }
  catch (e) {
    document.body.innerHTML = `<div class="empty">找不到该人物：${esc(e.message)}</div>`;
    return;
  }
  document.title = `${figure.name} · 对话`;
  document.documentElement.style.setProperty("--accent", figure.accent || "#2b4162");
  $("avatar").src = "/" + (figure.avatar || "");
  $("name").textContent = figure.name;
  $("era").textContent = figure.era || "";
  renderSources(); renderQuestions(); renderDilemmas(); renderQuickAsk(); resetChat(); await setupProviders(); loadProfile();
}

function renderSources() {
  const s = figure.sources || [];
  $("sources").innerHTML = s.length
    ? s.map(x => `<div class="item"><b>${esc(x.title || "")}</b><small>${esc(x.kind || "")}${x.note ? " · " + esc(x.note) : ""}</small></div>`).join("")
    : '<div class="empty">该人物尚未关联史料。</div>';
}

function renderQuestions() {
  const q = figure.suggested_questions || [];
  $("questions").innerHTML = q.length
    ? q.map(t => `<button class="qchip">${esc(t)}</button>`).join("")
    : '<div class="empty">暂无建议问题。</div>';
  $("questions").querySelectorAll(".qchip").forEach(b => {
    b.onclick = () => { $("input").value = b.textContent; $("input").focus(); };
  });
}

function resetChat() {
  messages = [];
  $("messages").innerHTML = "";
  if (figure.opening) addMsg("figure", figure.opening, false); // 开场白仅展示，不进入历史（兼容 Anthropic）
}

function addMsg(role, content, push = true) {
  const div = document.createElement("div");
  div.className = "msg " + role;
  if (role === "figure") fillFigureMsg(div, content);
  else div.textContent = content;
  $("messages").appendChild(div);
  $("messages").scrollTop = $("messages").scrollHeight;
  if (push) messages.push({ role: role === "user" ? "user" : "assistant", content });
}

async function send() {
  const text = $("input").value.trim();
  if (!text) return;
  $("input").value = "";
  addMsg("user", text);
  const holder = document.createElement("div");
  holder.className = "msg figure";
  holder.textContent = "……";
  $("messages").appendChild(holder);
  $("messages").scrollTop = $("messages").scrollHeight;
  try {
    const { reply } = await api("/api/chat", {
      method: "POST",
      body: JSON.stringify({
        figure_id: figure.id, messages, provider: cfg.provider,
        model: cfg.model, base_url: cfg.base_url, api_key: cfg.api_key,
      }),
    });
    fillFigureMsg(holder, reply);
    messages.push({ role: "assistant", content: reply });
  } catch (e) {
    holder.className = "msg sys";
    holder.textContent = "调用失败：" + e.message;
  }
  $("messages").scrollTop = $("messages").scrollHeight;
}

async function setupProviders() {
  const { providers } = await api("/api/providers");
  const sel = $("provider");
  sel.innerHTML = providers.map(p => `<option value="${p.id}">${esc(p.label)}</option>`).join("");
  sel.value = cfg.provider || "mock";
  applyDefaults(cfg, providers);
  sel.onchange = () => {
    const p = providers.find(x => x.id === sel.value);
    $("model").value = p?.default_model || "";
    $("base_url").value = p?.default_base_url || "";
    saveCfg();
  };
  ["model", "base_url", "api_key"].forEach(id => $(id).addEventListener("input", saveCfg));
}

function applyDefaults(c, providers) {
  const p = providers.find(x => x.id === (c.provider || "mock")) || providers[0];
  $("model").value = c.model || p.default_model || "";
  $("base_url").value = c.base_url || p.default_base_url || "";
  $("api_key").value = c.api_key || "";
}

function saveCfg() {
  cfg = { provider: $("provider").value, model: $("model").value, base_url: $("base_url").value, api_key: $("api_key").value };
  store.set("hs_api", cfg);
}

$("send").onclick = send;
$("newchat").onclick = resetChat;
$("input").addEventListener("keydown", e => { if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); send(); } });

boot();


/* ---------- 抉择任务（P0-1） ---------- */
const RUBRIC = [
  ["sourcing", "史料溯源"], ["contextualization", "语境化"], ["corroboration", "交叉验证"],
  ["argumentation", "论证"], ["historical_empathy", "历史共情"],
];
let activeDilemma = null;
let selfScores = {};
let hintLevel = 0;

function renderDilemmas() {
  const ds = figure.dilemmas || [];
  $("dilemmas").innerHTML = ds.length
    ? ds.map((d, i) => `<div class="dilemma-item">
        <div class="t"><b>${esc(d.title)}</b><small>${(d.options || []).length} 个选项</small></div>
        <button class="btn ghost" data-i="${i}">开始</button></div>`).join("")
    : '<div class="empty">该人物暂无抉择任务。</div>';
  $("dilemmas").querySelectorAll("button[data-i]").forEach(b => {
    b.onclick = () => openDilemma((figure.dilemmas || [])[+b.dataset.i]);
  });
}

function openDilemma(d) {
  activeDilemma = d;
  const hints = d.hints || (d.hint ? [d.hint] : []);
  selfScores = {};
  hintLevel = 0;
  $("mTitle").textContent = "抉择：" + d.title;
  $("mBody").innerHTML = `
    <div class="scenario">${esc(d.scenario || "")}</div>
    <div id="opts">${(d.options || []).map(o =>
      `<label class="opt"><input type="radio" name="choice" value="${esc(o.id)}"><span>${esc(o.text)}</span></label>`).join("")}</div>
    <div id="hintBox"></div>
    ${hints.length ? '<button type="button" class="btn ghost small" id="hintBtn">💡 需要一点提示？</button>' : ""}
    <div class="selfassess">
      <div class="mini">先自评：你觉得你的论证在这五方面各能得几分？（0–3，必填）</div>
      <div id="selfRows">${RUBRIC.map(([k, name]) => `
        <div class="self-row" data-k="${k}">
          <span class="self-name">${name}</span>
          <span class="chips">${[0, 1, 2, 3].map((v) =>
            `<button type="button" class="chip" data-v="${v}">${v}</button>`).join("")}</span>
        </div>`).join("")}</div>
    </div>
    <div style="font-size:13px;color:var(--muted)">你的论证——为什么这样选？最好引用史料作为依据。</div>
    <textarea id="argInput" placeholder="例如：我选择……，因为……（依据：《……》）"></textarea>
    <label class="toggle" style="margin-top:12px"><input type="checkbox" id="dbl">
      启用双评分（两次独立评分 + 一致性，更可靠，约 2 倍耗时）</label>
    <div class="row-actions"><button class="btn" id="mSubmit">提交论证</button>
      <span id="mStatus" style="align-self:center;color:var(--muted);font-size:13px"></span></div>
    <div id="mResult"></div>`;
  bindOpts();
  bindSelfAssess();
  bindHints(hints);
  $("mSubmit").onclick = submitDecision;
  $("modal").hidden = false;
}

async function submitDecision() {
  const chosen = $("mBody").querySelector('input[name="choice"]:checked');
  const argument = $("argInput").value.trim();
  if (!chosen) { $("mStatus").textContent = "请先选择一个选项"; return; }
  if (!argument) { $("mStatus").textContent = "请写下你的论证"; return; }
  const missing = RUBRIC.filter(([k]) => typeof selfScores[k] !== "number").length;
  if (missing) { $("mStatus").textContent = `请先完成自评（还差 ${missing} 项）`; return; }
  const usedHints = hintLevel;
  $("mStatus").textContent = "评估中…";
  try {
    const { result } = await api("/api/decide", {
      method: "POST",
      body: JSON.stringify({
        figure_id: figure.id, dilemma_id: activeDilemma.id, choice_id: chosen.value, argument,
        student_id: STUDENT, double_score: !!($("dbl") && $("dbl").checked),
        self_scores: selfScores, hints_used: usedHints,
        provider: cfg.provider, model: cfg.model, base_url: cfg.base_url, api_key: cfg.api_key,
      }),
    });
    $("mStatus").textContent = "";
    renderResult(result, selfScores, usedHints);
    loadProfile();
    const label = chosen.parentElement.querySelector("span").textContent;
    addMsg("sys", `【抉择 · ${activeDilemma.title}】你选择了「${label}」，论证已提交。`, false);
  } catch (e) {
    $("mStatus").textContent = "提交失败：" + e.message;
  }
}

function renderResult(r, selfScores, usedHints) {
  if (r.error) {
    $("mResult").innerHTML = `<div class="fb warn"><b>评估失败</b><br>${esc(r.error)}<br>${esc(r.raw || "")}</div>`;
    return;
  }
  const AG = { "高": "ag-high", "中": "ag-mid", "低": "ag-low" };
  const rows = RUBRIC.map(([k, name]) => {
    const ag = r.agreement && r.agreement[k]
      ? `<span class="ag ${AG[r.agreement[k]] || ""}">一致性 ${r.agreement[k]}</span>` : "";
    return `<div>${name}</div>
      <div><span class="bar"><i style="width:${(r.scores[k] / 3) * 100}%"></i></span>
      <b style="margin-left:8px">${r.scores[k]}/3</b>${ag}</div>`;
  }).join("");

  let cmp = "";
  if (selfScores && RUBRIC.some(([k]) => typeof selfScores[k] === "number")) {
    const gaps = [];
    const cmpRows = RUBRIC.map(([k, name]) => {
      const self = typeof selfScores[k] === "number" ? selfScores[k] : "—";
      const ai = typeof r.scores[k] === "number" ? r.scores[k] : "—";
      let gapTxt = "—", gapCls = "even";
      if (typeof self === "number" && typeof ai === "number") {
        const g = self - ai;
        gaps.push(g);
        gapTxt = g > 0 ? `+${g}` : `${g}`;
        gapCls = g > 0 ? "over" : (g < 0 ? "under" : "even");
      }
      return `<div>${name}</div><div>自评 <b>${self}</b> · AI <b>${ai}</b>
        <span class="gap ${gapCls}">${gapTxt}</span></div>`;
    }).join("");
    const avg = gaps.length ? gaps.reduce((a, b) => a + b, 0) / gaps.length : 0;
    const verdict = Math.abs(avg) < 0.34 ? "自评与 AI 评分基本一致。"
      : (avg > 0 ? `你整体高估了约 ${avg.toFixed(1)} 分。` : `你整体低估了约 ${Math.abs(avg).toFixed(1)} 分。`);
    cmp = `<div class="total" style="margin-top:18px">自评 vs AI</div>
      <div class="score-grid">${cmpRows}</div>
      <div class="fb">元认知提示：${verdict}</div>`;
  }

  const hintLine = usedHints
    ? `<div class="fb">本次使用了 <b>${usedHints}</b> 级提示（不扣分，仅供教师参考）。</div>` : "";

  $("mResult").innerHTML = `
    <hr style="border:none;border-top:1px solid var(--line);margin:22px 0 4px">
    <div class="total">总分 ${r.total} / ${r.max_total}</div>
    <div class="score-grid">${rows}</div>
    <div class="fb good"><b>👍 做得好</b><br>${(r.strengths || []).map(esc).join("<br>") || "—"}</div>
    <div class="fb warn"><b>🔧 可以改进</b><br>${(r.improvements || []).map(esc).join("<br>") || "—"}</div>
    <div class="fb"><b>点评</b><br>${esc(r.feedback || "")}</div>
    ${hintLine}
    ${cmp}
    ${r.needs_review ? '<div class="fb warn"><b>⚠️ 评分一致性偏低</b><br>该次评分的部分维度两次结果差异较大，建议教师复核或让学生补充论证后再评。</div>' : ""}`;
}

$("mClose").onclick = () => { $("modal").hidden = true; };
$("modal").addEventListener("click", (e) => { if (e.target.id === "modal") $("modal").hidden = true; });


/* ---------- 史料交叉验证（P0-2） ---------- */
let activeClaim = "";

function fillFigureMsg(div, content) {
  div.textContent = content;
  const btn = document.createElement("button");
  btn.className = "verify-btn";
  btn.textContent = "🔍 核对史料";
  btn.onclick = () => openCheck(content);
  div.appendChild(btn);
}

function bindOpts() {
  $("mBody").querySelectorAll(".opt").forEach(lab => {
    lab.querySelector("input").addEventListener("change", () => {
      $("mBody").querySelectorAll(".opt").forEach(x => x.classList.remove("sel"));
      lab.classList.add("sel");
    });
  });
}

function openCheck(claim) {
  activeClaim = claim;
  const sources = figure.sources || [];
  $("mTitle").textContent = "核对史料";
  $("mBody").innerHTML = `
    <div style="font-size:13px;color:var(--muted)">要核对的 AI 说法：</div>
    <div class="scenario">${esc(claim)}</div>
    <div style="font-size:13px;color:var(--muted);margin-bottom:8px">可对照的史料：</div>
    <div class="src">${sources.length ? sources.map(s => `<div class="item"><b>${esc(s.title || "")}</b>
        <small>${esc(s.kind || "")}${s.note ? " · " + esc(s.note) : ""}</small>
        ${s.excerpt ? `<div class="excerpt">${esc(s.excerpt)}</div>` : ""}</div>`).join("")
      : '<div class="empty">该人物尚未关联史料。</div>'}</div>
    <div style="font-size:13px;color:var(--muted);margin:18px 0 8px">这条说法与史料相符吗？</div>
    <div id="verdicts">
      <label class="opt"><input type="radio" name="verdict" value="相符"><span>相符</span></label>
      <label class="opt"><input type="radio" name="verdict" value="有出入"><span>有出入（夸大、偏差，或与史料矛盾）</span></label>
      <label class="opt"><input type="radio" name="verdict" value="史料未涉及"><span>史料未涉及</span></label>
    </div>
    <div style="font-size:13px;color:var(--muted);margin-top:12px">你的依据——依据哪一份史料？为什么？</div>
    <textarea id="argInput" placeholder="例如：依据《……》，其中说……，与该说法不同，因为……"></textarea>
    <div class="row-actions"><button class="btn" id="mSubmit">提交核对</button>
      <span id="mStatus" style="align-self:center;color:var(--muted);font-size:13px"></span></div>
    <div id="mResult"></div>`;
  bindOpts();
  $("mSubmit").onclick = submitCheck;
  $("modal").hidden = false;
}

async function submitCheck() {
  const v = $("mBody").querySelector('input[name="verdict"]:checked');
  const basis = $("argInput").value.trim();
  if (!v) { $("mStatus").textContent = "请先选择你的判断"; return; }
  if (!basis) { $("mStatus").textContent = "请写下你的依据"; return; }
  $("mStatus").textContent = "核对中…";
  try {
    const { result } = await api("/api/check", {
      method: "POST",
      body: JSON.stringify({
        figure_id: figure.id, claim: activeClaim, verdict: v.value, basis, student_id: STUDENT,
        provider: cfg.provider, model: cfg.model, base_url: cfg.base_url, api_key: cfg.api_key,
      }),
    });
    $("mStatus").textContent = "";
    renderCheckResult(result);
    addMsg("sys", `【史料核对】你的判断：${v.value}。`, false);
  } catch (e) {
    $("mStatus").textContent = "核对失败：" + e.message;
  }
}

function renderCheckResult(r) {
  if (r.error) {
    $("mResult").innerHTML = `<div class="fb warn"><b>核对失败</b><br>${esc(r.error)}<br>${esc(r.raw || "")}</div>`;
    return;
  }
  $("mResult").innerHTML = `
    <hr style="border:none;border-top:1px solid var(--line);margin:22px 0 4px">
    <div class="fb good"><b>你的判断：${esc(r.verdict || "")}</b><br>${esc(r.reason || "")}</div>
    ${r.suggestion ? `<div class="fb warn"><b>可以改进</b><br>${esc(r.suggestion)}</div>` : ""}
    ${r.reference ? `<div class="fb"><b>参照判断</b><br>${esc(r.reference)}</div>` : ""}`;
}


/* ---------- 历史思维画像（P0-3） ---------- */
async function loadProfile() {
  try {
    const { profile: p } = await api(`/api/profile?student_id=${encodeURIComponent(STUDENT)}`);
    renderProfile(p);
  } catch (e) { /* 静默失败，不打断对话 */ }
}

function renderProfile(p) {
  const box = $("profile");
  if (!box) return;
  if (!p || !p.count) {
    box.innerHTML = '<div class="empty">完成一次「抉择任务」后，这里会出现你的能力画像。</div>';
    return;
  }
  const bk = p.by_kind || {};
  const rows = RUBRIC.map(([k, name]) => {
    const d = p.per_dimension[k];
    const chip = d.level ? `<span class="lv lv-${d.level_key}">${esc(d.level)}</span>` : "";
    return `<div class="prof-row"><span>${name}</span>
      <span class="bar"><i style="width:${d.pct || 0}%"></i></span>
      <b>${d.avg == null ? "—" : d.avg}</b>${chip}</div>`;
  }).join("");
  const gapNote = (typeof p.overall_gap === "number" && Math.abs(p.overall_gap) >= 0.34)
    ? `<div class="fb warn" style="margin-top:10px">自评偏差：整体${p.overall_gap > 0 ? "高估" : "低估"}约 ${Math.abs(p.overall_gap).toFixed(1)} 分</div>` : "";
  box.innerHTML = `<div style="font-size:12.5px;color:var(--muted);margin-bottom:10px">
      抉择 ${bk.decision || 0} 次 · 核对 ${bk.check || 0} 次</div>
    ${rows}
    ${p.weakest ? `<div class="fb warn" style="margin-top:10px">最需要加强：<b>${esc(p.per_dimension[p.weakest].name)}</b></div>` : ""}
    ${gapNote}
    <button type="button" class="btn ghost small" id="guideBtn">📖 指标说明与水平划分</button>`;
  const gb = $("guideBtn");
  if (gb) gb.onclick = openGuide;
}

/* ---------- 指标说明（P0-5） ---------- */
let rubricGuide = null;

async function openGuide() {
  if (!rubricGuide) {
    try { rubricGuide = await api("/api/rubric"); }
    catch (e) { return; }
  }
  $("mTitle").textContent = "指标说明与水平划分";
  $("mBody").innerHTML = `
    <div style="font-size:13px;color:var(--muted);margin-bottom:10px">
      五个指标各 0–3 分。下面是它们的意思，以及不同分数段代表的水平。</div>
    <div class="level-strip">${rubricGuide.levels.map((l) => `
      <span class="lv lv-${l.key}">${esc(l.label)}
        <small>${l.min}–${l.max > 3 ? 3 : l.max} 分</small></span>`).join("")}</div>
    <div class="guard-grid">${rubricGuide.dimensions.map((d) => `
      <div class="gcard"><b>${esc(d.name)}</b><p>${esc(d.meaning)}</p>
        <div class="gl"><span class="tag low">低</span>${esc(d.low)}</div>
        <div class="gl"><span class="tag high">高</span>${esc(d.high)}</div>
      </div>`).join("")}</div>`;
  $("modal").hidden = false;
}

/* ---------- 快捷追问（P0-4） ---------- */
function renderQuickAsk() {
  $("quickask").innerHTML = QUICK_ASKS.map((q) =>
    `<button type="button" class="qask">${esc(q)}</button>`).join("");
  $("quickask").querySelectorAll(".qask").forEach((b) => {
    b.onclick = () => { $("input").value = b.textContent; $("input").focus(); };
  });
}

/* ---------- 自评与分级支架（P0-4） ---------- */
function bindSelfAssess() {
  $("selfRows").querySelectorAll(".self-row").forEach((row) => {
    const k = row.dataset.k;
    row.querySelectorAll(".chip").forEach((chip) => {
      chip.onclick = () => {
        row.querySelectorAll(".chip").forEach((c) => c.classList.remove("on"));
        chip.classList.add("on");
        selfScores[k] = +chip.dataset.v;
      };
    });
  });
}

function bindHints(hints) {
  const btn = $("hintBtn");
  if (!btn) return;
  btn.onclick = () => {
    if (hintLevel >= hints.length) return;
    const div = document.createElement("div");
    div.className = "hintline";
    div.textContent = `💡 提示 ${hintLevel + 1}：${hints[hintLevel]}`;
    $("hintBox").appendChild(div);
    hintLevel += 1;
    if (hintLevel >= hints.length) {
      btn.textContent = "已给出全部提示";
      btn.disabled = true;
    } else {
      btn.textContent = `💡 再给一点提示？（已用 ${hintLevel}/${hints.length}）`;
    }
  };
}
