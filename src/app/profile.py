# -*- coding: utf-8 -*-
"""历史思维画像（P0-3）：把学生的抉择评分汇总成能力画像。"""
from .assessment import MAX_PER_ITEM, RUBRIC

DIM_NAMES = {key: name for key, name, _ in RUBRIC}


def build_profile(rows):
    keys = [key for key, _, _ in RUBRIC]
    sums = {k: 0 for k in keys}
    counts = {k: 0 for k in keys}
    for row in rows:
        scores = (row.get("result") or {}).get("scores") or {}
        for k in keys:
            value = scores.get(k)
            if isinstance(value, (int, float)):
                sums[k] += value
                counts[k] += 1

    per_dimension = {}
    for k in keys:
        per_dimension[k] = {
            "name": DIM_NAMES[k],
            "avg": round(sums[k] / counts[k], 2) if counts[k] else None,
            "n": counts[k],
            "max": MAX_PER_ITEM,
            "pct": round(sums[k] / (counts[k] * MAX_PER_ITEM) * 100) if counts[k] else 0,
        }

    scored = [(k, v["avg"]) for k, v in per_dimension.items() if v["avg"] is not None]
    weakest = min(scored, key=lambda x: x[1])[0] if scored else None
    strongest = max(scored, key=lambda x: x[1])[0] if scored else None
    return {
        "count": len(rows),
        "per_dimension": per_dimension,
        "weakest": weakest,
        "strongest": strongest,
    }
