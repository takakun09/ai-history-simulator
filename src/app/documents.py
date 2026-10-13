# -*- coding: utf-8 -*-
"""人物设定文档文本抽取（P0-7）。

支持 .md / .txt / .docx；只做纯文本抽取，不落盘。
"""
import base64
import binascii
import html
import io
import re
import zipfile

TEXT_EXT = ("md", "markdown", "txt")
DOCX_EXT = ("docx",)
ALLOWED = TEXT_EXT + DOCX_EXT
MAX_BYTES = 5 * 1024 * 1024
MAX_CHARS = 8000

ERROR_TEXT = {
    "unsupported_type": "只支持 .md / .txt / .docx 文档",
    "too_large": "文档太大，请控制在 5MB 以内",
    "bad_data": "文档内容读取失败",
}


class ExtractError(ValueError):
    """args[0] 为错误码，便于前端做多语言。"""


def _ext(filename):
    match = re.search(r"\.([A-Za-z0-9]+)$", filename or "")
    return match.group(1).lower() if match else ""


def _decode(data):
    if not isinstance(data, str) or not data:
        raise ExtractError("bad_data")
    payload = data.split(",", 1)[1] if data.startswith("data:") and "," in data else data
    payload = re.sub(r"\s+", "", payload)
    if len(payload) > MAX_BYTES * 4 // 3 + 4096:
        raise ExtractError("too_large")
    try:
        raw = base64.b64decode(payload, validate=True)
    except (binascii.Error, ValueError):
        raise ExtractError("bad_data") from None
    if not raw:
        raise ExtractError("bad_data")
    if len(raw) > MAX_BYTES:
        raise ExtractError("too_large")
    return raw


def _docx_text(raw):
    try:
        with zipfile.ZipFile(io.BytesIO(raw)) as zf:
            xml = zf.read("word/document.xml").decode("utf-8", "replace")
    except (zipfile.BadZipFile, KeyError):
        raise ExtractError("bad_data") from None
    xml = re.sub(r"</w:p>", "\n", xml)          # 段落 → 换行
    text = re.sub(r"<[^>]+>", "", xml)          # 去标签
    return html.unescape(text)


def extract_text(filename, data):
    ext = _ext(filename)
    if ext not in ALLOWED:
        raise ExtractError("unsupported_type")
    raw = _decode(data)
    if ext in TEXT_EXT:
        text = raw.decode("utf-8", "replace")
    else:
        text = _docx_text(raw)
    text = re.sub(r"[ \t]+\n", "\n", text)
    text = re.sub(r"\n{3,}", "\n\n", text).strip()
    if not text:
        raise ExtractError("bad_data")
    return text[:MAX_CHARS]
