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


def _rubric_text():
    return "\n".join(f"- {k}（{name}）：{desc}" for k, name, desc in RUBRIC)


def build_messages(figure, dilemma, choice_text, argument):
    system = (
        "你是一位严格但友善的历史教学评估助手。依据给定量表评价学生对历史抉择的论证，"
        "并给出可操作的改进建议。只输出 JSON，不要输出任何其它文字。"
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


def evaluate(provider_id, base_url, api_key, model, figure, dilemma, choice_text, argument):
    if provider_id == "mock":
        return _mock(argument)
    system, user = build_messages(figure, dilemma, choice_text, argument)
    reply = providers.chat(
        provider_id, base_url, api_key, model, system,
        [{"role": "user", "content": user}], figure_name=figure.get("name", ""),
    )
    return parse_result(reply)
