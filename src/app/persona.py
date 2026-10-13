# -*- coding: utf-8 -*-
"""人物限制词生成（P0-7）。

两种模式：
- template：不依赖任何模型，用统一模板把老师的几句话补成结构完整的限制词（开箱即用兜底）
- ai：交给模型按同一套结构写得更自然、更贴合人物；结构不完整时自动回退到 template
"""
import json
import re

from . import providers

# 一份合格限制词必须覆盖的四块（与 seed.py 里的三个人物保持一致）
SECTIONS = ("身份与立场", "知识边界", "作为有立场者", "教学约束")

TEMPLATE = """你是{name}（{era}），{role}。
【身份与立场】{stance}
【知识边界】你的认知止于{era}。你不知道此后发生的事情，也不知道现代的事物；被问到超出你时代的问题，以当时人的口吻表示无从知晓，不要强行解释。
【作为有立场者】你并不全知，也不总是正确。你会为自己的判断辩护，也会流露对他人与局势的态度。学生若质疑你，你可以坚持，也可以承认顾虑。
【教学约束】
- 你是历史模拟中的「当事人」，不是百科；允许展现立场与时代局限。
- 学生追问史料依据时，可以提及你熟悉的文献，但不要编造原文。
- 不替学生下结论；引导学生自己思考、自己查证。
- {limit}，语气符合你的身份。"""

DEFAULTS = {
    "role": "一位身处历史现场的人物",
    "stance": "你按自己的信念行事，对局势有自己的判断。",
    "student_role": "一名前来请教的年轻人",
    "limit": "每次回答控制在 120 字以内",
}

AI_SYSTEM = (
    "你是历史教学场景的提示词工程师。请把老师提供的人物信息，写成一段给大语言模型的"
    "「人物扮演限制词」。必须完整包含四个部分：【身份与立场】【知识边界】【作为有立场者】"
    "【教学约束】。要求：写明该人物不知道未来之事、允许有立场与时代局限、不替学生下结论、"
    "回答有字数上限。只输出限制词正文，不要任何解释或标题。"
)


def _clean(fields, key, default=""):
    value = (fields or {}).get(key)
    value = value.strip() if isinstance(value, str) else ""
    return value or default


def build_template(fields):
    """纯规则：把老师的几句话补成结构完整的限制词。"""
    limit = _clean(fields, "limit", DEFAULTS["limit"])
    # 老师可能只填「120 字」或「>150 字」，补成完整的一句约束
    if "回答" not in limit and not limit.startswith("每次"):
        limit = f"每次回答控制在 {limit}"
    return TEMPLATE.format(
        name=_clean(fields, "name", "这位历史人物"),
        era=_clean(fields, "era", "其所处时代"),
        role=_clean(fields, "role", DEFAULTS["role"]),
        stance=_clean(fields, "stance", DEFAULTS["stance"]),
        limit=limit,
    )


def missing_sections(text):
    return [s for s in SECTIONS if f"【{s}】" not in (text or "")]


def build_ai_messages(fields, brief):
    student_role = _clean(fields, "student_role", DEFAULTS["student_role"])
    user = f"""【人物】{_clean(fields, 'name', '（未提供）')}
【时代】{_clean(fields, 'era', '（未提供）')}
【身份】{_clean(fields, 'role', '（未提供）')}
【主要立场】{_clean(fields, 'stance', '（未提供）')}
【学生在本对话中扮演】{student_role}
【老师提供的补充资料】
{(brief or '').strip()[:4000] or '（无）'}

请据此写出这段人物扮演限制词。"""
    return AI_SYSTEM, user


def generate(provider_id, base_url, api_key, model, fields, brief="", mode="template"):
    """返回 {"prompt": str, "mode": "template"|"ai", "note": str|None}"""
    if mode == "ai" and provider_id and provider_id != "mock":
        try:
            system, user = build_ai_messages(fields, brief)
            text = providers.chat(provider_id, base_url, api_key, model, system,
                                  [{"role": "user", "content": user}]).strip()
            text = re.sub(r"^```[a-zA-Z]*\n?|\n?```$", "", text).strip()
            if text and not missing_sections(text):
                return {"prompt": text, "mode": "ai", "note": None}
            fallback = build_template(fields)
            return {"prompt": fallback, "mode": "template",
                    "note": "模型返回缺少必需章节，已改用模板生成"}
        except Exception as exc:  # 网络/额度问题都不该让老师卡住
            return {"prompt": build_template(fields), "mode": "template",
                    "note": f"AI 生成失败（{type(exc).__name__}），已改用模板生成"}
    return {"prompt": build_template(fields), "mode": "template", "note": None}
