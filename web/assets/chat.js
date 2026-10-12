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
  renderSources(); renderQuestions(); resetChat(); await setupProviders();
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
  div.textContent = content;
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
    holder.textContent = reply;
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
