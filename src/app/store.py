# -*- coding: utf-8 -*-
"""人物数据的持久化（data/figures.json）。"""
import json
import threading
from pathlib import Path

from .seed import DEFAULT_FIGURES

ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT / "data"
FIGURES_FILE = DATA_DIR / "figures.json"
_lock = threading.Lock()


def _write(figs):
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    tmp = FIGURES_FILE.with_suffix(".tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(figs, f, ensure_ascii=False, indent=2)
    tmp.replace(FIGURES_FILE)


def _read():
    if not FIGURES_FILE.exists():
        _write(DEFAULT_FIGURES)
    with open(FIGURES_FILE, encoding="utf-8") as f:
        return json.load(f)


def list_figures(published_only=False):
    with _lock:
        figs = _read()
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
        figs = _read()
        for i, f in enumerate(figs):
            if f.get("id") == fig.get("id"):
                figs[i] = {**f, **fig}
                break
        else:
            figs.append(fig)
        _write(figs)
    return get_figure(fig.get("id"))


def delete_figure(fid):
    with _lock:
        figs = _read()
        kept = [f for f in figs if f.get("id") != fid]
        _write(kept)
    return len(kept) != len(figs)
