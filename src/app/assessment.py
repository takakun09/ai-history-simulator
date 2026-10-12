# -*- coding: utf-8 -*-
"""历史抉择的论证评估（P0-1：抉择节点 + 论证提交）。

用 LLM 按历史思维量表给学生论证打分。P0-3 会在此基础上深化。
"""
import json
import re

from . import providers

RUBRIC = [
    ("sourcing", "史料溯源", "是否追问或标注信息的来源与立场"),
    ("contextualization", "语境化", "是否把决策放回当时的时代背景"),
    ("corroboration", "交叉验证", "是否对照多个来源而非只听一家之言"),
    ("argumentation", "论证", "是否给出「论点—证据—推理」"),
    ("historical_empathy", "历史共情", "是否理解当时人的处境与限制"),
]
MAX_PER_ITEM = 3
# 史料核对只评这三个维度
CHECK_DIMENSIONS = ("sourcing", "corroboration", "argumentation")

# 界面切到英文 / 繁体时，让模型用对应语言写评语
LANG_NOTE = {
    "en": "\nPlease write all of your feedback (reason/comment) in English.",
    "tw": "\n請使用繁體中文撰寫所有評語。",
}


def _rubric_text():
    return "\n".join(f"- {k}（{name}）：{desc}" for k, name, desc in RUBRIC)


def build_messages(figure, dilemma, choice_text, argument, lang="zh"):
    system = (
        "你是一位严格但友善的历史教学评估助手。依据给定量表评价学生对历史抉择的论证，"
        "并给出可操作的改进建议。只输出 JSON，不要输出任何其它文字。"
        + LANG_NOTE.get(lang or "zh", "")
    )
    options = " / ".join(o.get("text", "") for o in dilemma.get("options", []))
    user = f"""【评分量表】每个维度 0–{MAX_PER_ITEM} 分：
{_rubric_text()}

【历史人物】{figure.get("name", "")}
【情境】{dilemma.get("scenario", "")}
【可选项】{options}
【学生的选择】{choice_text}
【学生的论证】{argument}

请严格按以下 JSON 结构输出（分数为 0–{MAX_PER_ITEM} 的整数）：
{{"scores":{{"sourcing":0,"contextualization":0,"corroboration":0,"argumentation":0,"historical_empathy":0}},
"strengths":["..."],"improvements":["..."],"feedback":"两到三句话的中文点评"}}"""
    return system, user


def parse_result(text):
    match = re.search(r"\{.*\}", text or "", re.S)
    if not match:
        return {"error": "无法解析模型返回", "raw": (text or "")[:500]}
    try:
        data = json.loads(match.group(0))
    except json.JSONDecodeError:
        return {"error": "无法解析模型返回", "raw": (text or "")[:500]}
    scores = data.get("scores") or {}
    clean = {}
    for key, _, _ in RUBRIC:
        try:
            clean[key] = max(0, min(MAX_PER_ITEM, int(scores.get(key, 0))))
        except (TypeError, ValueError):
            clean[key] = 0
    data["scores"] = clean
    data["total"] = sum(clean.values())
    data["max_total"] = len(RUBRIC) * MAX_PER_ITEM
    return data


def _mock(argument):
    n = len(argument or "")
    base = 2 if n >= 80 else 1
    scores = {k: base for k, _, _ in RUBRIC}
    scores["corroboration"] = 0 if n < 120 else 1
    return {
        "scores": scores,
        "total": sum(scores.values()),
        "max_total": len(RUBRIC) * MAX_PER_ITEM,
        "strengths": ["立场明确"], "improvements": ["补充具体史料出处", "说明当时的时代背景"],
        "feedback": "（离线演示反馈）你的论证方向清楚，但还缺少史料依据与时代背景。"
                    "试着引用至少两份史料，并说明当时人面临的实际限制。",
    }


def _score_once(provider_id, base_url, api_key, model, figure, dilemma, choice_text, argument,
                temperature, lang="zh"):
    system, user = build_messages(figure, dilemma, choice_text, argument, lang)
    reply = providers.chat(
        provider_id, base_url, api_key, model, system,
        [{"role": "user", "content": user}], figure_name=figure.get("name", ""),
        temperature=temperature,
    )
    return parse_result(reply)


def _merge(first, second):
    """两次独立评分的均值 + 逐维一致性（评分信度）。"""
    a = first.get("scores") or {}
    b = second.get("scores") or {}
    merged, agreement = {}, {}
    for key, _, _ in RUBRIC:
        va, vb = int(a.get(key, 0)), int(b.get(key, 0))
        merged[key] = round((va + vb) / 2)
        diff = abs(va - vb)
        agreement[key] = "高" if diff == 0 else ("中" if diff == 1 else "低")
    out = dict(first)
    out["scores"] = merged
    out["total"] = sum(merged.values())
    out["max_total"] = len(RUBRIC) * MAX_PER_ITEM
    out["agreement"] = agreement
    out["passes"] = [a, b]
    out["needs_review"] = any(v == "低" for v in agreement.values())
    return out


def evaluate(provider_id, base_url, api_key, model, figure, dilemma, choice_text, argument,
             double_score=False, lang="zh"):
    """评估学生论证。double_score=True 时做两次独立评分并给出一致性。"""
    if provider_id == "mock":
        result = _mock(argument)
        result["agreement"] = None
        result["needs_review"] = False
        return result

    first = _score_once(provider_id, base_url, api_key, model, figure, dilemma,
                        choice_text, argument, temperature=0.0, lang=lang)
    if first.get("error") or not double_score:
        first["agreement"] = None
        first["needs_review"] = False
        return first

    second = _score_once(provider_id, base_url, api_key, model, figure, dilemma,
                         choice_text, argument, temperature=0.5, lang=lang)
    if second.get("error"):
        first["agreement"] = None
        first["needs_review"] = False
        return first
    return _merge(first, second)


# ---------------------------------------------------------------------------
# 史料核对（P0-2）
# ---------------------------------------------------------------------------
def _sources_text(sources):
    lines = []
    for s in sources or []:
        line = f"- {s.get('title', '')}（{s.get('kind', '')}）"
        if s.get("excerpt"):
            line += f"：{s['excerpt']}"
        lines.append(line)
    return "\n".join(lines) or "（该人物暂无史料）"


def parse_check(text):
    match = re.search(r"\{.*\}", text or "", re.S)
    if not match:
        return {"error": "无法解析模型返回", "raw": (text or "")[:400]}
    try:
        data = json.loads(match.group(0))
    except json.JSONDecodeError:
        return {"error": "无法解析模型返回", "raw": (text or "")[:400]}
    raw = data.get("scores") or {}
    clean = {}
    for key in CHECK_DIMENSIONS:          # 只保留这三个维度，缺失的不写入
        if key in raw:
            try:
                clean[key] = max(0, min(MAX_PER_ITEM, int(raw[key])))
            except (TypeError, ValueError):
                continue
    data["scores"] = clean
    return data


def _mock_check(verdict, basis):
    ok = len(basis or "") >= 40
    return {
        "verdict": "站得住" if ok else "部分成立",
        "reason": "你给出了明确判断，并陈述了依据。" if ok else "你有判断，但依据还不够具体。",
        "suggestion": "" if ok else "指出具体是哪一份史料、哪一句与这段说法有关。",
        "reference": "（离线演示）请对照史料摘要，自行判断这段说法属于「相符」「有出入」还是「史料未涉及」。",
        "scores": {k: (2 if ok else 1) for k in CHECK_DIMENSIONS},
    }


def check_source(provider_id, base_url, api_key, model, figure, claim, verdict, basis,
                 lang="zh"):
    if provider_id == "mock":
        return _mock_check(verdict, basis)
    system = (
        "你是历史教学中的「史料裁判」。学生正在核对一段 AI 历史人物的说法是否与史料相符。"
        "请判断学生的判断是否站得住，并给出改进建议。只输出 JSON，不要输出其它文字。"
        + LANG_NOTE.get(lang or "zh", "")
    )
    user = f"""【AI 的历史人物说法】{claim}

【可对照的史料】
{_sources_text(figure.get("sources", []))}

【学生的判断】{verdict}
【学生的依据】{basis}

请只输出 JSON：
{{"verdict":"站得住|部分成立|站不住","reason":"为什么（中文，2-3 句）",
"suggestion":"如何改进核查（中文，1-2 句）","reference":"关于这段说法与史料关系的参照判断（中文，1-2 句）",
"scores":{{"sourcing":0,"corroboration":0,"argumentation":0}}}}
其中 scores 是学生在这次核对中表现出的三种能力，各 0-{MAX_PER_ITEM} 分：
sourcing=是否追到具体史料与出处；corroboration=是否做了来源之间的比对；
argumentation=依据与判断之间是否有推理。"""
    reply = providers.chat(
        provider_id, base_url, api_key, model, system,
        [{"role": "user", "content": user}], figure_name=figure.get("name", ""),
    )
    return parse_check(reply)
