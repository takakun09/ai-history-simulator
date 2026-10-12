import { api, esc } from "/assets/app.js";

const $ = (id) => document.getElementById(id);
let figures = [];
let current = null;

async function load() {
  const r = await api("/api/figures?scope=teacher");
  figures = r.figures;
  renderList();
  if (figures.length) select(current && figures.some(f => f.id === current) ? current : figures[0].id);
  else blank();
}

function renderList() {
  $("list").innerHTML = figures.map(f => `
    <div class="fig-item ${current === f.id ? "active" : ""}" data-id="${esc(f.id)}">
      <img src="/${esc(f.avatar || "")}" alt="">
      <div class="t"><b>${esc(f.name)}</b><small>${esc(f.era || "")}</small></div>
      <span class="badge ${f.published ? "on" : "off"}">${f.published ? "已发布" : "未发布"}</span>
    </div>`).join("") || '<div class="empty">还没有人物。</div>';
  $("list").querySelectorAll(".fig-item").forEach(el => { el.onclick = () => select(el.dataset.id); });
}

function fill(f) {
  $("f_id").value = f.id || ""; $("f_name").value = f.name || ""; $("f_name_en").value = f.name_en || "";
  $("f_era").value = f.era || ""; $("f_difficulty").value = f.difficulty || ""; $("f_accent").value = f.accent || "#2b4162";
  $("f_tagline").value = f.tagline || ""; $("f_avatar").value = f.avatar || ""; $("f_opening").value = f.opening || "";
  $("f_prompt").value = f.system_prompt || "";
  $("f_sources").value = (f.sources || []).map(s => [s.title || "", s.kind || "", s.note || ""].join(" | ")).join("\n");
  $("f_questions").value = (f.suggested_questions || []).join("\n");
  $("f_published").checked = !!f.published;
  $("title").textContent = f.name ? `编辑：${f.name}` : "新建历史人物";
  $("test").href = f.id ? `/chat?figure=${encodeURIComponent(f.id)}` : "#";
  $("status").textContent = "";
}

function select(id) {
  current = id;
  const f = figures.find(x => x.id === id);
  renderList();
  if (f) fill(f);
}

function blank() {
  current = null;
  renderList();
  fill({ accent: "#2b4162", published: false, id: "", avatar: "assets/avatars/placeholder.svg" });
  $("title").textContent = "新建历史人物";
}

function collect() {
  return {
    id: $("f_id").value.trim(), name: $("f_name").value.trim(), name_en: $("f_name_en").value.trim(),
    era: $("f_era").value.trim(), difficulty: $("f_difficulty").value.trim(), accent: $("f_accent").value.trim(),
    tagline: $("f_tagline").value.trim(), avatar: $("f_avatar").value.trim(), opening: $("f_opening").value,
    system_prompt: $("f_prompt").value,
    sources: $("f_sources").value.split("\n").map(l => l.trim()).filter(Boolean).map(l => {
      const [title, kind, note] = l.split("|").map(s => (s || "").trim());
      return { title, kind, note };
    }),
    suggested_questions: $("f_questions").value.split("\n").map(l => l.trim()).filter(Boolean),
    published: $("f_published").checked,
  };
}

async function save() {
  const fig = collect();
  if (!fig.id) { $("status").textContent = "⚠️ 请填写唯一 ID（英文）"; return; }
  try {
    await api("/api/figures", { method: "POST", body: JSON.stringify(fig) });
    $("status").textContent = "✅ 已保存并发布";
    current = fig.id;
    await load();
  } catch (e) { $("status").textContent = "保存失败：" + e.message; }
}

async function del() {
  if (!current) return;
  if (!confirm("确认删除该历史人物？此操作不可撤销。")) return;
  try {
    await api(`/api/figures/${encodeURIComponent(current)}`, { method: "DELETE" });
    current = null;
    await load();
  } catch (e) { $("status").textContent = "删除失败：" + e.message; }
}

$("save").onclick = save;
$("del").onclick = del;
$("new").onclick = blank;
load();
