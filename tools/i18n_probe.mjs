class T { constructor(v){ this.nodeType=3; this.nodeValue=v; this.parentElement={closest:()=>null}; } }
class E { constructor(k=[]){ this.nodeType=1; this.childNodes=k; this._a={}; this._d={}; }
  matches(){return false;} hasAttribute(k){return k in this._a;} getAttribute(k){return this._a[k]??null;}
  setAttribute(k,v){this._a[k]=v;} get dataset(){return this._d;} }
const cases = ["开始","选择：王平——谨慎持重","编辑：诸葛亮","一致性 高","请先完成自评（还差 3 项）",
               "本次使用了 ","级提示（不扣分，仅供教师参考）。","元认知提示：你整体高估了约 0.8 分。",
               "自评偏差：整体低估约 1.2 分","最需要加强：","史料溯源"];
const nodes = cases.map(c => new T(c));
global.localStorage = { getItem: () => "en", setItem: () => {} };
global.MutationObserver = class { observe(){} };
global.document = { readyState:"complete", title:"x", documentElement:{}, body:new E(nodes),
  querySelector:()=>null, addEventListener:()=>{} };
const m = await import(new URL("../web/assets/i18n.js", import.meta.url).href);
m.applyI18n();
cases.forEach((c,i)=>console.log(`${c}  ->  ${nodes[i].nodeValue}`));
