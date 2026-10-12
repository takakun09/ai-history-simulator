# -*- coding: utf-8 -*-
"""历史思维画像（P0-3 / P0-4）：汇总抉择评分与史料核对，并给出自评偏差。"""
from .assessment import MAX_PER_ITEM, RUBRIC

DIM_NAMES = {key: name for key, name, _ in RUBRIC}


def build_profile(rows):
    """rows 可以是抉择记录或核对记录；缺少字段一律跳过，不抛异常。"""
    keys = [key for key, _, _ in RUBRIC]
    sums = {k: 0 for k in keys}
    counts = {k: 0 for k in keys}
    self_sums = {k: 0 for k in keys}
    self_counts = {k: 0 for k in keys}
    by_kind = {}

    for row in rows:
        kind = row.get("kind") or "other"
        by_kind[kind] = by_kind.get(kind, 0) + 1

        scores = (row.get("result") or {}).get("scores") or {}
        for k in keys:
            value = scores.get(k)
            if isinstance(value, (int, float)):
                sums[k] += value
                counts[k] += 1

        self_scores = row.get("self_scores") or {}
        for k in keys:
            value = self_scores.get(k)
            if isinstance(value, (int, float)):
                self_sums[k] += value
                self_counts[k] += 1

    per_dimension = {}
    gaps = []
    for k in keys:
        avg = round(sums[k] / counts[k], 2) if counts[k] else None
        self_avg = round(self_sums[k] / self_counts[k], 2) if self_counts[k] else None
        gap = round(self_avg - avg, 2) if (avg is not None and self_avg is not None) else None
        if gap is not None:
            gaps.append(gap)
        per_dimension[k] = {
            "name": DIM_NAMES[k],
            "avg": avg,
            "self_avg": self_avg,
            "gap": gap,
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
        "by_kind": {"decision": by_kind.get("decision", 0), "check": by_kind.get("check", 0)},
        "overall_gap": round(sum(gaps) / len(gaps), 2) if gaps else None,
    }
