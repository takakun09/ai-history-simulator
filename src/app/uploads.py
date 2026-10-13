# -*- coding: utf-8 -*-
"""人物形象上传（P0-6）。

只接受常见位图格式，单张上限 2 MB；不支持 SVG（避免脚本注入）。
落盘到 web/assets/avatars/uploads/，由现有静态文件处理直接服务。
"""
import base64
import binascii
import re
import uuid
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
WEB = ROOT / "web"

UPLOAD_DIR = WEB / "assets" / "avatars" / "uploads"   # 模块级，测试可注入临时目录
URL_PREFIX = "assets/avatars/uploads"
ALLOWED = ("png", "jpg", "jpeg", "webp", "gif")
MAX_BYTES = 2 * 1024 * 1024

ERROR_TEXT = {
    "unsupported_type": "只支持 PNG / JPG / WEBP / GIF 图片",
    "too_large": "图片太大，请压缩到 2MB 以内",
    "bad_data": "图片数据读取失败",
}


class UploadError(ValueError):
    """参数不合法；args[0] 是错误码，便于前端做多语言。"""


def _ext(filename):
    match = re.search(r"\.([A-Za-z0-9]+)$", filename or "")
    return match.group(1).lower() if match else ""


def save_image(filename, data):
    ext = _ext(filename)
    if ext not in ALLOWED:
        raise UploadError("unsupported_type")
    if not isinstance(data, str) or not data:
        raise UploadError("bad_data")

    payload = data.split(",", 1)[1] if data.startswith("data:") and "," in data else data
    payload = re.sub(r"\s+", "", payload)

    # 解码前先按 base64 长度粗筛，避免把超大 payload 解进内存
    if len(payload) > MAX_BYTES * 4 // 3 + 4096:
        raise UploadError("too_large")

    try:
        raw = base64.b64decode(payload, validate=True)
    except (binascii.Error, ValueError):
        raise UploadError("bad_data") from None
    if not raw:
        raise UploadError("bad_data")
    if len(raw) > MAX_BYTES:
        raise UploadError("too_large")

    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    name = f"{uuid.uuid4().hex}.{ext}"
    (UPLOAD_DIR / name).write_bytes(raw)
    return f"{URL_PREFIX}/{name}"
