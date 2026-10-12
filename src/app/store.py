# -*- coding: utf-8 -*-
"""数据持久化。

- seed.py 是「默认内容」的唯一来源，并带 SEED_VERSION；
  存储文件的版本与代码不一致时，按 seed 重建（演示阶段简化：会覆盖教师端改动）。
- 学生提交（抉择论证、史料核对）追加保存在 data/ 下。
"""
import copy
import json
import threading
from pathlib import Path

from .seed import DEFAULT_FIGURES, SEED_VERSION

ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT / "data"
FIGURES_FILE = DATA_DIR / "figures.json"
SUBMISSIONS_FILE = DATA_DIR / "submissions.json"
CHECKS_FILE = DATA_DIR / "checks.json"
_lock = threading.Lock()


def _read_json(path, default):
    if not path.exists():
        return default
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def _write_json(path, obj):
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(".tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)
    tmp.replace(path)


# ---------- 历史人物 ----------
def _read_figures():
    data = _read_json(FIGURES_FILE, None)
    if data is None:
        _write_figures(DEFAULT_FIGURES)
        return copy.deepcopy(DEFAULT_FIGURES)
    if isinstance(data, list):  # 旧格式：纯列表
        data = {"seed_version": None, "figures": data}
    if data.get("seed_version") != SEED_VERSION:
        _write_figures(DEFAULT_FIGURES)
        return copy.deepcopy(DEFAULT_FIGURES)
    return data.get("figures", [])


def _write_figures(figs):
    _write_json(FIGURES_FILE, {"seed_version": SEED_VERSION, "figures": figs})


def list_figures(published_only=False):
    with _lock:
        figs = _read_figures()
    if published_only:
        figs = [f for f in figs if f.get("published")]
    return figs


def get_figure(fid):
    for f in list_figures():
        if f.get("id") == fid:
            return f
    return None


def upsert_figure(fig):
    with _lock:
        figs = _read_figures()
        for i, f in enumerate(figs):
            if f.get("id") == fig.get("id"):
                figs[i] = {**f, **fig}
                break
        else:
            figs.append(fig)
        _write_figures(figs)
    return get_figure(fig.get("id"))


def delete_figure(fid):
    with _lock:
        figs = _read_figures()
        kept = [f for f in figs if f.get("id") != fid]
        _write_figures(kept)
    return len(kept) != len(figs)


# ---------- 通用记录（抉择提交 / 史料核对） ----------
def _append(path, rec):
    with _lock:
        rows = _read_json(path, [])
        rows.append(rec)
        _write_json(path, rows)
    return rec


def save_submission(rec):
    return _append(SUBMISSIONS_FILE, rec)


def list_submissions():
    with _lock:
        return _read_json(SUBMISSIONS_FILE, [])


def save_check(rec):
    return _append(CHECKS_FILE, rec)


def list_checks():
    with _lock:
        return _read_json(CHECKS_FILE, [])
