import { api, esc, store } from "/assets/app.js";

const $ = (id) => document.getElementById(id);
const SOURCE_KINDS = ["一手", "二手", "正史", "文献", "图像", "考古"];
const EDITOR = document.querySelector(".editor");

let figures = [];
let current = null;
let draft = null;
let savedSnapshot = "";

/* ---------------- 加载与列表 ---------------- */
async function load() {
  const r = await api("/api/figures?scope=teacher");
  figures = r.figures;
  renderList();
  if (figures.length) select(figures.some((f) => f.id === current) ? current : figures[0].id, true);
  else blank(true);
}

function renderList() {
  $("list").innerHTML = figures.map((f) => `
    <div class="fig-item ${current === f.id ? "active" : ""}" data-id="${esc(f.id)}">
      <img src="/${esc(f.avatar || "")}" alt="">
      <div class="t"><b>${esc(f.name)}</b><small>${esc(f.era || "")}</small></div>
      <span class="badge ${f.published ? "on" : "off"}">${f.published ? "已发布" : "未发布"}</span>
    </div>`).join("") || '<div class="empty">还没有人物。</div>';
  $("list").querySelectorAll(".fig-item").forEach((el) => { el.onclick = () => select(el.dataset.id); });
}

function select(id, force = false) {
  if (!force && current !== id && !confirmDiscard("切换人物")) return renderList();
  current = id;
  renderList();
  const f = figures.find((x) => x.id === id);
  if (f) fill(f);
}

function blank(force = false) {
  if (!force && !confirmDiscard("新建人物")) return;
  current = null;
  renderList();
  fill({
    id: "", name: "", name_en: "", era: "", difficulty: "入门", accent: "#2b4162",
    tagline: "", avatar: "assets/avatars/placeholder.svg", opening: "", system_prompt: "",
    sources: [], suggested_questions: [], dilemmas: [], published: false,
  });
  $("title").textContent = "新建历史人物";
}

/* ---------------- 未保存提醒 ---------------- */
function isDirty() {
  if (!draft || !savedSnapshot) return false;
  try { return JSON.stringify(collect()) !== savedSnapshot; } catch { return false; }
}

function refreshDirty() {
  const base = draft && draft.name ? `编辑：${draft.name}` : "新建历史人物";
  $("title").textContent = isDirty() ? base + " · ● 未保存" : base;
  if (isDirty()) $("status").textContent = "有未保存的修改";
}

function confirmDiscard(action) {
  if (!isDirty()) return true;
  return confirm(`当前有未保存的修改，${action}后将丢失。确定继续吗？`);
}

window.addEventListener("beforeunload", (e) => {
  if (isDirty()) { e.preventDefault(); e.returnValue = ""; }
});

/* ---------------- 填充 ---------------- */
function fill(f) {
  draft = JSON.parse(JSON.stringify(f));
  draft.sources = draft.sources || [];
  draft.suggested_questions = draft.suggested_questions || [];
  draft.dilemmas = draft.dilemmas || [];

  $("f_id").value = draft.id || "";
  $("f_name").value = draft.name || "";
  $("f_name_en").value = draft.name_en || "";
  $("f_era").value = draft.era || "";
  $("f_difficulty").value = ["入门", "进阶", "挑战"].includes(draft.difficulty) ? draft.difficulty : "入门";
  $("f_accent").value = draft.accent || "#2b4162";
  $("f_accent_color").value = /^#[0-9a-fA-F]{6}$/.test(draft.accent || "") ? draft.accent : "#2b4162";
  $("f_tagline").value = draft.tagline || "";
  $("f_avatar").value = draft.avatar || "";
  updateAvatarPreview();
  avatarMsg("");
  $("f_opening").value = draft.opening || "";
  $("f_prompt").value = draft.system_prompt || "";
  $("wz_name").value = draft.name || "";
  $("wz_era").value = draft.era || "";
  $("f_published").checked = !!draft.published;
  $("test").href = draft.id ? `/chat?figure=${encodeURIComponent(draft.id)}` : "#";
  $("status").textContent = "";

  renderSources();
  renderQuestions();
  renderDilemmas();
  switchTab("basic");
  savedSnapshot = JSON.stringify(collect());
  refreshDirty();
}

function switchTab(name) {
  document.querySelectorAll(".tab").forEach((t) => t.classList.toggle("active", t.dataset.tab === name));
  document.querySelectorAll(".tabpane").forEach((p) => p.classList.toggle("active", p.id === "pane-" + name));
}
document.querySelectorAll(".tab").forEach((t) => { t.onclick = () => switchTab(t.dataset.tab); });

function updateCounts() {
  $("cntSources").textContent = draft.sources.length;
  $("cntQuestions").textContent = draft.suggested_questions.length;
  $("cntDilemmas").textContent = draft.dilemmas.length;
}

/* ---------------- 拖拽排序 ---------------- */
let dragItem = null, dragContainer = null, dragSelector = null, dragOnDone = null;

function getDragAfterElement(container, y, selector) {
  const els = [...container.querySelectorAll(`${selector}:not(.dragging)`)];
  return els.reduce((closest, child) => {
    const box = child.getBoundingClientRect();
    const offset = y - box.top - box.height / 2;
    return offset < 0 && offset > closest.offset ? { offset, element: child } : closest;
  }, { offset: Number.NEGATIVE_INFINITY, element: null }).element;
}

function makeSortable(container, selector, onDone) {
  container.querySelectorAll(selector).forEach((item) => {
    const handle = item.querySelector(".drag-handle");
    if (!handle) return;
    handle.draggable = true;
    handle.addEventListener("dragstart", (e) => {
      dragItem = item; dragContainer = container; dragSelector = selector; dragOnDone = onDone;
      item.classList.add("dragging");
      e.dataTransfer.effectAllowed = "move";
      try { e.dataTransfer.setData("text/plain", ""); } catch (_) { /* ignore */ }
    });
    handle.addEventListener("dragend", () => {
      item.classList.remove("dragging");
      if (dragContainer === container && typeof dragOnDone === "function") {
        onDone([...container.querySelectorAll(selector)].map((el) => +el.dataset.i));
      }
      dragItem = dragContainer = dragOnDone = null;
    });
  });
  if (!container._dragBound) {
    container._dragBound = true;
    container.addEventListener("dragover", (e) => {
      if (!dragItem || dragContainer !== container) return;
      e.preventDefault();
      const after = getDragAfterElement(container, e.clientY, dragSelector);
      if (after == null) container.appendChild(dragItem);
      else container.insertBefore(dragItem, after);
    });
  }
}

/* ---------------- 史料 ---------------- */
const isCustomKind = (k) => !!k && !SOURCE_KINDS.includes(k);

function kindOptionsHtml(kind) {
  const sel = kind || SOURCE_KINDS[0];
  const known = SOURCE_KINDS.map((k) =>
    `<option value="${esc(k)}" ${k === sel ? "selected" : ""}>${esc(k)}</option>`).join("");
  return known + `<option value="__custom__" ${isCustomKind(kind) ? "selected" : ""}>自定义…</option>`;
}

const HANDLE = '<span class="drag-handle" title="拖拽排序">⠿</span>';

function renderSources() {
  $("sourcesList").innerHTML = draft.sources.map((s, i) => `
    <div class="list-row sortable-item" data-i="${i}">
      <div class="rowhead">
        ${HANDLE}
        <input class="grow" data-k="title" value="${esc(s.title || "")}" placeholder="史料标题，如《出师表》">
        <button class="icon-btn" data-act="del-source" title="删除这份史料">✕</button>
      </div>
      <div class="grid2">
        <div><span class="mini">类型</span>
          <select data-k="kind">${kindOptionsHtml(s.kind)}</select>
          <input data-k="kind_custom" class="kind-custom" placeholder="输入自定义类型"
                 value="${isCustomKind(s.kind) ? esc(s.kind) : ""}" ${isCustomKind(s.kind) ? "" : "hidden"}>
        </div>
        <div><span class="mini">备注</span>
          <input data-k="note" value="${esc(s.note || "")}" placeholder="如：核心一手史料"></div>
      </div>
      <div><span class="mini">摘要 / 可对照原文（学生核对时看到）</span>
        <textarea data-k="excerpt" rows="2" placeholder="填原文节选或要点">${esc(s.excerpt || "")}</textarea></div>
    </div>`).join("") || '<div class="empty">还没有史料，点下面按钮添加。</div>';

  $("sourcesList").querySelectorAll(".list-row").forEach((row) => {
    const i = +row.dataset.i;
    row.querySelectorAll("[data-k]").forEach((el) => {
      const handler = () => { onSourceInput(i, el); refreshDirty(); };
      el.addEventListener("input", handler);
      el.addEventListener("change", handler);
    });
    row.querySelector('[data-act="del-source"]').onclick = () => {
      draft.sources.splice(i, 1); renderSources(); updateCounts(); refreshDirty();
    };
  });
  makeSortable($("sourcesList"), ".sortable-item", (order) => {
    draft.sources = order.map((i) => draft.sources[i]); renderSources(); refreshDirty();
  });
  updateCounts();
}

function onSourceInput(i, el) {
  const s = draft.sources[i];
  const k = el.dataset.k;
  if (k === "kind") {
    const custom = el.parentElement.querySelector('[data-k="kind_custom"]');
    if (el.value === "__custom__") { custom.hidden = false; custom.focus(); s.kind = custom.value; }
    else { custom.hidden = true; custom.value = ""; s.kind = el.value; }
    return;
  }
  if (k === "kind_custom") { s.kind = el.value; return; }
  s[k] = el.value;
}

/* ---------------- 建议问题 ---------------- */
function renderQuestions() {
  $("questionsList").innerHTML = draft.suggested_questions.map((q, i) => `
    <div class="list-row sortable-item" data-i="${i}">
      <div class="rowhead">
        ${HANDLE}
        <input class="grow" data-k="q" value="${esc(q || "")}" placeholder="如：丞相，您为何执意北伐？">
        <button class="icon-btn" data-act="del-q" title="删除">✕</button>
      </div>
    </div>`).join("") || '<div class="empty">还没有问题，点下面按钮添加。</div>';

  $("questionsList").querySelectorAll(".list-row").forEach((row) => {
    const i = +row.dataset.i;
    row.querySelector("[data-k=q]").addEventListener("input", (e) => {
      draft.suggested_questions[i] = e.target.value; refreshDirty();
    });
    row.querySelector('[data-act="del-q"]').onclick = () => {
      draft.suggested_questions.splice(i, 1); renderQuestions(); updateCounts(); refreshDirty();
    };
  });
  makeSortable($("questionsList"), ".sortable-item", (order) => {
    draft.suggested_questions = order.map((i) => draft.suggested_questions[i]); renderQuestions(); refreshDirty();
  });
  updateCounts();
}

/* ---------------- 抉择节点 ---------------- */
function renderDilemmas() {
  $("dilemmasList").innerHTML = draft.dilemmas.map((d, i) => `
    <div class="dilemma-card sortable-item" data-i="${i}">
      <div class="rowhead">
        ${HANDLE}
        <input class="grow" data-k="title" value="${esc(d.title || "")}" placeholder="抉择标题，如：街亭用人">
        <button class="icon-btn" data-act="del-dilemma" title="删除这个抉择">✕</button>
      </div>
      <span class="mini">情境</span>
      <textarea data-k="scenario" rows="3" placeholder="给学生描述这个历史抉择场景">${esc(d.scenario || "")}</textarea>
      <span class="mini">提示（分级支架，最多 3 级，每行一级；越往下越具体，但始终不给答案）</span>
      <textarea data-k="hints" rows="3" placeholder="第 1 级：给一个方向&#10;第 2 级：给一个比较&#10;第 3 级：点出关键约束">${esc((d.hints || (d.hint ? [d.hint] : [])).join("\n"))}</textarea>
      <span class="mini">选项（可拖拽排序）</span>
      <div data-opts>
        ${(d.options || []).map((o, j) => `
          <div class="opt-row sortable-item" data-i="${j}">
            ${HANDLE}
            <input data-ok="text" value="${esc(o.text || "")}" placeholder="选项内容">
            <button class="icon-btn" data-act="del-option" title="删除选项">✕</button>
          </div>`).join("")}
      </div>
      <button class="add-btn small" data-act="add-option">＋ 添加选项</button>
    </div>`).join("") || '<div class="empty">还没有抉择节点，点下面按钮添加。</div>';

  $("dilemmasList").querySelectorAll(".dilemma-card").forEach((card) => {
    const i = +card.dataset.i;
    card.querySelectorAll("[data-k]").forEach((el) => {
      el.addEventListener("input", () => {
        if (el.dataset.k === "hints") {
          draft.dilemmas[i].hints = el.value.split("\n")
            .map((x) => x.trim()).filter(Boolean).slice(0, 3);
        } else {
          draft.dilemmas[i][el.dataset.k] = el.value;
        }
        refreshDirty();
      });
    });
    card.querySelector('[data-act="del-dilemma"]').onclick = () => {
      draft.dilemmas.splice(i, 1); renderDilemmas(); updateCounts(); refreshDirty();
    };
    card.querySelector('[data-act="add-option"]').onclick = () => {
      draft.dilemmas[i].options = draft.dilemmas[i].options || [];
      draft.dilemmas[i].options.push({ id: "opt" + (draft.dilemmas[i].options.length + 1), text: "" });
      renderDilemmas(); refreshDirty();
    };
    const optBox = card.querySelector("[data-opts]");
    optBox.querySelectorAll(".opt-row").forEach((rowEl) => {
      const j = +rowEl.dataset.i;
      rowEl.querySelector("[data-ok=text]").addEventListener("input", (e) => {
        draft.dilemmas[i].options[j].text = e.target.value; refreshDirty();
      });
      rowEl.querySelector('[data-act="del-option"]').onclick = () => {
        draft.dilemmas[i].options.splice(j, 1); renderDilemmas(); refreshDirty();
      };
    });
    makeSortable(optBox, ".sortable-item", (order) => {
      const opts = draft.dilemmas[i].options;
      draft.dilemmas[i].options = order.map((j) => opts[j]); renderDilemmas(); refreshDirty();
    });
  });
  updateCounts();
}

/* ---------------- 保存 ---------------- */
function collect() {
  return {
    id: $("f_id").value.trim(),
    name: $("f_name").value.trim(),
    name_en: $("f_name_en").value.trim(),
    era: $("f_era").value.trim(),
    difficulty: $("f_difficulty").value,
    accent: $("f_accent").value.trim() || "#2b4162",
    tagline: $("f_tagline").value.trim(),
    avatar: $("f_avatar").value.trim(),
    opening: $("f_opening").value,
    system_prompt: $("f_prompt").value,
    published: $("f_published").checked,
    sources: draft.sources
      .map((s) => ({ title: (s.title || "").trim(), kind: (s.kind || "").trim(),
                     note: (s.note || "").trim(), excerpt: (s.excerpt || "").trim() }))
      .filter((s) => s.title),
    suggested_questions: draft.suggested_questions.map((q) => (q || "").trim()).filter(Boolean),
    dilemmas: draft.dilemmas.map((d, i) => ({
      id: d.id || "d" + (i + 1),
      title: (d.title || "").trim(),
      scenario: (d.scenario || "").trim(),
      hints: (d.hints || []).map((x) => (x || "").trim()).filter(Boolean).slice(0, 3),
      rubric_focus: d.rubric_focus || [],
      options: (d.options || [])
        .map((o, j) => ({ id: o.id || "opt" + (j + 1), text: (o.text || "").trim() }))
        .filter((o) => o.text),
    })).filter((d) => d.title && d.options.length),
  };
}

async function save() {
  const fig = collect();
  if (!fig.id) { $("status").textContent = "⚠️ 请填写唯一 ID（英文）"; switchTab("basic"); return; }
  try {
    await api("/api/figures", { method: "POST", body: JSON.stringify(fig) });
    current = fig.id;
    await load();
    $("status").textContent = "✅ 已保存并发布";
  } catch (e) { $("status").textContent = "保存失败：" + e.message; }
}

async function del() {
  if (!current) return;
  if (!confirm("确认删除该历史人物？此操作不可撤销。")) return;
  try {
    await api(`/api/figures/${encodeURIComponent(current)}`, { method: "DELETE" });
    current = null; await load();
  } catch (e) { $("status").textContent = "删除失败：" + e.message; }
}

/* ---------------- 事件绑定 ---------------- */
$("addSource").onclick = () => { draft.sources.push({ title: "", kind: "一手", note: "", excerpt: "" }); renderSources(); refreshDirty(); };
$("addQuestion").onclick = () => { draft.suggested_questions.push(""); renderQuestions(); refreshDirty(); };
$("addDilemma").onclick = () => {
  draft.dilemmas.push({ id: "d" + (draft.dilemmas.length + 1), title: "", scenario: "", hint: "",
                        rubric_focus: [], options: [{ id: "opt1", text: "" }, { id: "opt2", text: "" }] });
  renderDilemmas(); switchTab("dilemmas"); refreshDirty();
};
$("save").onclick = save;
$("del").onclick = del;
$("new").onclick = () => blank();

$("f_accent_color").addEventListener("input", (e) => { $("f_accent").value = e.target.value; refreshDirty(); });
$("f_accent").addEventListener("input", (e) => {
  if (/^#[0-9a-fA-F]{6}$/.test(e.target.value)) $("f_accent_color").value = e.target.value;
  refreshDirty();
});
EDITOR.addEventListener("input", refreshDirty);
EDITOR.addEventListener("change", refreshDirty);

load();


/* ---------- 形象拖拽上传（P0-6） ---------- */
const AVATAR_OK = ["image/png", "image/jpeg", "image/webp", "image/gif"];
const AVATAR_MAX = 2 * 1024 * 1024;
const UPLOAD_ERR = {
  unsupported_type: "只支持 PNG / JPG / WEBP / GIF 图片",
  too_large: "图片太大，请压缩到 2MB 以内",
  bad_data: "图片数据读取失败",
  io_error: "形象上传失败",
};

function avatarMsg(text, ok) {
  const el = $("avatarMsg");
  if (!el) return;
  el.textContent = text || "";
  el.classList.toggle("ok", !!ok);
  el.classList.toggle("bad", !!text && !ok);
}

function updateAvatarPreview() {
  const img = $("avatarPreview");
  if (!img) return;
  const path = ($("f_avatar").value || "").trim() || "assets/avatars/placeholder.svg";
  img.src = "/" + path.replace(/^\/+/, "");
}

async function uploadAvatar(file) {
  if (!file) return;
  if (!AVATAR_OK.includes(file.type)) { avatarMsg(UPLOAD_ERR.unsupported_type); return; }
  if (file.size > AVATAR_MAX) { avatarMsg(UPLOAD_ERR.too_large); return; }
  avatarMsg("上传中…");
  try {
    const data = await new Promise((resolve, reject) => {
      const fr = new FileReader();
      fr.onload = () => resolve(fr.result);
      fr.onerror = () => reject(new Error("read"));
      fr.readAsDataURL(file);
    });
    const resp = await api("/api/upload", {
      method: "POST",
      body: JSON.stringify({ filename: file.name, data }),
    });
    $("f_avatar").value = resp.path;
    if (draft) draft.avatar = resp.path;
    updateAvatarPreview();
    avatarMsg("上传成功", true);
    refreshDirty();
  } catch (e) {
    avatarMsg(UPLOAD_ERR[(e && e.code) || ""] || UPLOAD_ERR.io_error);
  }
}

function initAvatarDrop() {
  const drop = $("avatarDrop");
  const file = $("avatarFile");
  if (!drop || !file) return;
  drop.onclick = () => file.click();
  drop.onkeydown = (e) => {
    if (e.key === "Enter" || e.key === " ") { e.preventDefault(); file.click(); }
  };
  file.onchange = () => { uploadAvatar(file.files[0]); file.value = ""; };
  ["dragenter", "dragover"].forEach((ev) =>
    drop.addEventListener(ev, (e) => { e.preventDefault(); drop.classList.add("dragover"); }));
  ["dragleave", "drop"].forEach((ev) =>
    drop.addEventListener(ev, (e) => { e.preventDefault(); drop.classList.remove("dragover"); }));
  drop.addEventListener("drop", (e) => {
    const f = e.dataTransfer && e.dataTransfer.files && e.dataTransfer.files[0];
    uploadAvatar(f);
  });
  $("f_avatar").addEventListener("input", updateAvatarPreview);
}

initAvatarDrop();
initWizard();
initDocDrop();


/* ---------- 人物限制词向导（P0-7） ---------- */
let docText = "";

function noteMsg(id, text, ok) {
  const el = $(id);
  if (!el) return;
  el.textContent = text || "";
  el.classList.toggle("ok", !!ok);
  el.classList.toggle("bad", !!text && !ok);
}

function wzFields() {
  return {
    name: $("wz_name").value.trim(),
    era: $("wz_era").value.trim(),
    role: $("wz_role").value.trim(),
    stance: $("wz_stance").value.trim(),
    student_role: $("wz_student").value.trim(),
    limit: $("wz_limit").value.trim(),
  };
}

async function generatePersona(mode, brief) {
  noteMsg("wzMsg", "生成中…");
  const cfg = store.get("hs_api", {});
  try {
    const r = await api("/api/persona", {
      method: "POST",
      body: JSON.stringify({
        fields: wzFields(), mode, brief: brief || "",
        provider: cfg.provider || "mock", model: cfg.model || "",
        base_url: cfg.base_url || "", api_key: cfg.api_key || "",
      }),
    });
    $("f_prompt").value = r.prompt;
    if (draft) draft.system_prompt = r.prompt;
    const base = r.mode === "ai" ? "AI 已生成" : "已按模板生成";
    noteMsg("wzMsg", r.note ? `${base}（${r.note}）` : base, true);
    refreshDirty();
  } catch (e) {
    noteMsg("wzMsg", "生成失败：" + e.message);
  }
}

async function initWizard() {
  try {
    const { providers } = await api("/api/providers");
    const sel = $("wz_provider");
    sel.innerHTML = providers.map((p) => `<option value="${p.id}">${esc(p.label)}</option>`).join("");
    const cfg = store.get("hs_api", { provider: "mock", model: "", base_url: "", api_key: "" });
    sel.value = cfg.provider || "mock";
    const cur = providers.find((p) => p.id === sel.value) || providers[0];
    $("wz_model").value = cfg.model || cur.default_model || "";
    $("wz_key").value = cfg.api_key || "";

    const save = () => {
      const p = providers.find((x) => x.id === sel.value) || providers[0];
      store.set("hs_api", {
        provider: sel.value, model: $("wz_model").value,
        base_url: p.default_base_url || "", api_key: $("wz_key").value,
      });
    };
    sel.addEventListener("change", () => {
      const p = providers.find((x) => x.id === sel.value) || providers[0];
      $("wz_model").value = p.default_model || "";
      save();
    });
    ["wz_model", "wz_key"].forEach((id) => $(id).addEventListener("input", save));
  } catch (e) { /* 拿不到接口列表也不影响模板生成 */ }

  $("wzGen").onclick = () => generatePersona("template");
  $("wzGenAi").onclick = () => generatePersona("ai");
  // 基本信息里的姓名/时代自动带过来，老师不用填两遍
  $("f_name").addEventListener("input", () => { $("wz_name").value = $("f_name").value; });
  $("f_era").addEventListener("input", () => { $("wz_era").value = $("f_era").value; });
}

/* ---------- 人物设定文档导入（P0-7） ---------- */
const DOC_ERR = {
  unsupported_type: "只支持 .md / .txt / .docx 文档",
  too_large: "文档太大，请控制在 5MB 以内",
  bad_data: "文档内容读取失败",
};

function showDoc(text) {
  docText = text || "";
  $("docPreview").value = docText;
  $("docPreview").hidden = !docText;
  $("docActions").hidden = !docText;
}

async function handleDoc(file) {
  if (!file) return;
  noteMsg("docMsg", "读取中…");
  try {
    const data = await new Promise((resolve, reject) => {
      const fr = new FileReader();
      fr.onload = () => resolve(fr.result);
      fr.onerror = () => reject(new Error("read"));
      fr.readAsDataURL(file);
    });
    const r = await api("/api/extract", {
      method: "POST",
      body: JSON.stringify({ filename: file.name, data }),
    });
    showDoc(r.text);
    noteMsg("docMsg", "文档已读取，可查看后选择如何使用", true);
  } catch (e) {
    noteMsg("docMsg", DOC_ERR[(e && e.code) || ""] || "文档读取失败");
  }
}

function initDocDrop() {
  const drop = $("docDrop");
  const file = $("docFile");
  if (!drop || !file) return;
  drop.onclick = () => file.click();
  drop.onkeydown = (e) => {
    if (e.key === "Enter" || e.key === " ") { e.preventDefault(); file.click(); }
  };
  file.onchange = () => { handleDoc(file.files[0]); file.value = ""; };
  ["dragenter", "dragover"].forEach((ev) =>
    drop.addEventListener(ev, (e) => { e.preventDefault(); drop.classList.add("dragover"); }));
  ["dragleave", "drop"].forEach((ev) =>
    drop.addEventListener(ev, (e) => { e.preventDefault(); drop.classList.remove("dragover"); }));
  drop.addEventListener("drop", (e) => {
    const f = e.dataTransfer && e.dataTransfer.files && e.dataTransfer.files[0];
    handleDoc(f);
  });

  $("docUse").onclick = () => {
    $("f_prompt").value = docText;
    if (draft) draft.system_prompt = docText;
    noteMsg("docMsg", "已填入限制词", true);
    refreshDirty();
  };
  $("docPolish").onclick = () => generatePersona("ai", docText);
}
