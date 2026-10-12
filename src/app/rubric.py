# -*- coding: utf-8 -*-
"""历史思维维度说明与水平划分（全项目单一定义源）。

学生端与教师端都从这里取文案与分段，避免两处各写一套。
"""

DIMENSION_GUIDE = [
    {
        "key": "sourcing", "name": "史料溯源",
        "meaning": "你是否追问或说明一条说法的来源、作者是谁、有什么立场。",
        "low": "直接接受结论，不问出处。",
        "high": "主动指出来源，并考虑作者的立场与时代。",
    },
    {
        "key": "contextualization", "name": "语境化",
        "meaning": "你是否把决定放回当时的时间与条件下考虑，而不是用今天的标准去衡量。",
        "low": "以今度古，忽略当时的处境。",
        "high": "结合当时的国力、地理、制度等约束来解释选择。",
    },
    {
        "key": "corroboration", "name": "交叉验证",
        "meaning": "你是否用多于一份的来源互相比对，而不是只听一家之言。",
        "low": "只凭单一来源或单一印象下判断。",
        "high": "主动对照两份以上史料，并指出它们的异同。",
    },
    {
        "key": "argumentation", "name": "论证",
        "meaning": "你的结论是否有「论点—证据—推理」的完整链条。",
        "low": "只给结论，或只有一句简单理由。",
        "high": "论点明确，引用具体证据，并说明证据如何支持结论。",
    },
    {
        "key": "historical_empathy", "name": "历史共情",
        "meaning": "你是否能理解当时人为什么会那样选择（理解不等于认同）。",
        "low": "用现在的是非直接评判古人。",
        "high": "能说出当时人的处境与限制，并据此解释其动机。",
    },
]

LEVELS = [
    {"key": "start", "label": "起步", "min": 0.0, "max": 0.75, "desc": "还很少体现，需要示范与练习。"},
    {"key": "basic", "label": "初步", "min": 0.75, "max": 1.5, "desc": "偶尔能做到，但不稳定。"},
    {"key": "good", "label": "较好", "min": 1.5, "max": 2.5, "desc": "多数时候能做到。"},
    {"key": "mature", "label": "成熟", "min": 2.5, "max": 3.01, "desc": "稳定而自觉地做到。"},
]


def level_for(avg):
    """把 0–3 的平均分映射到水平档位；无数据返回 None。"""
    if avg is None:
        return None
    for lv in LEVELS:
        if lv["min"] <= avg < lv["max"]:
            return lv
    return LEVELS[-1]


def guide_payload():
    return {"dimensions": DIMENSION_GUIDE, "levels": LEVELS, "max": 3}
