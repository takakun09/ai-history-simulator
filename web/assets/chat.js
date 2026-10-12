import { api, qs, esc, store } from "/assets/app.js";

const $ = (id) => document.getElementById(id);
const figId = qs("figure");
let figure = null;
let messages = [];
let cfg = store.get("hs_api", { provider: "mock", model: "", base_url: "", api_key: "" });

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
  renderSources(); renderQuestions(); renderDilemmas(); resetChat(); await setupProviders();
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
  $("mTitle").textContent = "抉择：" + d.title;
  $("mBody").innerHTML = `
    <div class="scenario">${esc(d.scenario || "")}</div>
    <div id="opts">${(d.options || []).map(o =>
      `<label class="opt"><input type="radio" name="choice" value="${esc(o.id)}"><span>${esc(o.text)}</span></label>`).join("")}</div>
    ${d.hint ? `<div class="hintline">💡 ${esc(d.hint)}</div>` : ""}
    <div style="font-size:13px;color:var(--muted)">你的论证——为什么这样选？最好引用史料作为依据。</div>
    <textarea id="argInput" placeholder="例如：我选择……，因为……（依据：《……》）"></textarea>
    <div class="row-actions"><button class="btn" id="mSubmit">提交论证</button>
      <span id="mStatus" style="align-self:center;color:var(--muted);font-size:13px"></span></div>
    <div id="mResult"></div>`;
  bindOpts();
  $("mSubmit").onclick = submitDecision;
  $("modal").hidden = false;
}

async function submitDecision() {
  const chosen = $("mBody").querySelector('input[name="choice"]:checked');
  const argument = $("argInput").value.trim();
  if (!chosen) { $("mStatus").textContent = "请先选择一个选项"; return; }
  if (!argument) { $("mStatus").textContent = "请写下你的论证"; return; }
  $("mStatus").textContent = "评估中…";
  try {
    const { result } = await api("/api/decide", {
      method: "POST",
      body: JSON.stringify({
        figure_id: figure.id, dilemma_id: activeDilemma.id, choice_id: chosen.value, argument,
        provider: cfg.provider, model: cfg.model, base_url: cfg.base_url, api_key: cfg.api_key,
      }),
    });
    $("mStatus").textContent = "";
    renderResult(result);
    const label = chosen.parentElement.querySelector("span").textContent;
    addMsg("sys", `【抉择 · ${activeDilemma.title}】你选择了「${label}」，论证已提交。`, false);
  } catch (e) {
    $("mStatus").textContent = "提交失败：" + e.message;
  }
}

function renderResult(r) {
  if (r.error) {
    $("mResult").innerHTML = `<div class="fb warn"><b>评估失败</b><br>${esc(r.error)}<br>${esc(r.raw || "")}</div>`;
    return;
  }
  const rows = RUBRIC.map(([k, name]) => `
    <div>${name}</div>
    <div><span class="bar"><i style="width:${(r.scores[k] / 3) * 100}%"></i></span>
      <b style="margin-left:8px">${r.scores[k]}/3</b></div>`).join("");
  $("mResult").innerHTML = `
    <hr style="border:none;border-top:1px solid var(--line);margin:22px 0 4px">
    <div class="total">总分 ${r.total} / ${r.max_total}</div>
    <div class="score-grid">${rows}</div>
    <div class="fb good"><b>👍 做得好</b><br>${(r.strengths || []).map(esc).join("<br>") || "—"}</div>
    <div class="fb warn"><b>🔧 可以改进</b><br>${(r.improvements || []).map(esc).join("<br>") || "—"}</div>
    <div class="fb"><b>点评</b><br>${esc(r.feedback || "")}</div>`;
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
        figure_id: figure.id, claim: activeClaim, verdict: v.value, basis,
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
