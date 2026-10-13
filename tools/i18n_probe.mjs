// i18n 冒烟测试：最小 DOM 桩，验证「静态结构 / 动态渲染 / 还原 / 不误翻」
class T { constructor(v){ this.nodeType=3; this.nodeValue=v; this.parentElement={closest:()=>null}; } }
class E {
  constructor(tag, kids=[]){ this.nodeType=1; this.tagName=tag; this.childNodes=kids; this._a={}; }
  matches(){ return false; }
  hasAttribute(k){ return k in this._a; }
  getAttribute(k){ return this._a[k] ?? null; }
  setAttribute(k,v){ this._a[k]=v; }
}
const el = (tag, kids) => new E(tag, kids);
const text = (v) => new T(v);
const kids = (e) => e.childNodes;

// 真实页面结构：header（顶栏）+ main（正文）
const brand = text("AI 历史人物模拟器");
const navHome = text("学生端");
const navAnalytics = text("学情分析");
const header = el("header", [el("div", [brand]), el("nav", [navHome, navAnalytics])]);

const h1 = text("学情分析");                       // 与导航同文案，正文里也必须翻
const hero = text("汇总学生在「抉择任务」中的论证评分，观察历史思维各维度的整体表现与个体差异。");
const dimName = text("史料溯源");
const level = text("起步");
const content = text("这是学生自己写的内容，不应被翻译");
const main = el("main", [el("div", [h1, hero]), el("div", [dimName, level, content])]);

const body = el("body", [header, main]);

let moCallback = null;
globalThis.localStorage = { getItem: () => "en", setItem: () => {} };
globalThis.MutationObserver = class { constructor(cb){ moCallback = cb; } observe(){} disconnect(){} };
globalThis.document = {
  readyState: "complete",
  title: "学情分析 · AI 历史人物模拟器",
  documentElement: {},
  body,
  querySelector: () => null,
  addEventListener: () => {},
};

const m = await import(new URL("../web/assets/i18n.js", import.meta.url).href);
m.applyI18n();
const expected = [
  [brand, "AI Historical Figure Simulator"],
  [navHome, "Student"],
  [navAnalytics, "Analytics"],
  [h1, "Analytics"],                                  // ← 之前就是这条没翻
  [hero, "Aggregated argument scores from decision tasks, across the five historical-thinking dimensions."],
  [dimName, "Sourcing"],
  [level, "Starting"],
  [content, "这是学生自己写的内容，不应被翻译"],
];
let fail = 0;
console.log(`title -> ${document.title}`);
for (const [node, want] of expected) {
  const got = node.nodeValue;
  const ok = got === want;
  if (!ok) fail += 1;
  console.log(`${ok ? "PASS" : "FAIL"}  ${got}`);
}

// 动态渲染：模拟 analytics.js 之后才插入内容 + observer 触发
const dyn = text("抉择提交");
body.childNodes.push(el("div", [dyn]));
if (moCallback) moCallback();
await new Promise((r) => setTimeout(r, 60));
console.log(`${dyn.nodeValue === "Decisions" ? "PASS" : "FAIL"}  动态渲染 -> ${dyn.nodeValue}`);
if (dyn.nodeValue !== "Decisions") fail += 1;

// ---- 含变量的界面字符串（曾漏翻的一类）----
const dynCases = [
  ["3 个选项", "3 option(s)"],
  ["平均提示级数（0% 用过提示）", "Avg. hints used (0% used hints)"],
  ["平均提示级数（无数据）", "Avg. hints used (no data)"],
  ["你的判断：站得住", "Your judgement: 站得住"],
  ["总分 9 / 15", "Total 9 / 15"],
  ["抉择 3 次 · 核对 2 次", "3 decision(s) · 2 check(s)"],
  ["用了 2 级提示", "used 2 hint(s)"],
  ["选择：王平", "Choice: 王平"],
  ["资料与任务", "Resources & tasks"],
  ["拖拽图片到此处，或点击选择", "Drag an image here, or click to choose"],
  ["只支持 PNG / JPG / WEBP / GIF 图片", "Only PNG / JPG / WEBP / GIF are supported"],
  ["上传中…", "Uploading…"],
];
for (const [input, want] of dynCases) {
  const n = text(input);
  body.childNodes.push(el("div", [n]));
  applyI18n();
  const ok = n.nodeValue === want;
  if (!ok) fail += 1;
  console.log(`${ok ? "PASS" : "FAIL"}  ${input} -> ${n.nodeValue}`);
}

// 切回中文应完整还原
m.setLang("zh");
for (const [node, want] of [[h1, "学情分析"], [hero, "汇总学生在「抉择任务」中的论证评分，观察历史思维各维度的整体表现与个体差异。"], [level, "起步"]]) {
  const ok = node.nodeValue === want;
  if (!ok) fail += 1;
  console.log(`${ok ? "PASS" : "FAIL"}  还原 -> ${node.nodeValue}`);
}

console.log(fail === 0 ? "\n全部通过 ✅" : `\n失败 ${fail} 项 ❌`);
process.exit(fail === 0 ? 0 : 1);
