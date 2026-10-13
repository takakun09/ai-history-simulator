# -*- coding: utf-8 -*-
"""限制词生成与文档抽取测试（P0-7）。"""
import base64
import io
import json
import unittest
import zipfile
from unittest import mock

from src.app import documents, persona, server


def post(path, payload):
    body = json.dumps(payload).encode("utf-8")
    h = server.Handler.__new__(server.Handler)
    h.path = path
    h.headers = {"Content-Length": str(len(body))}
    h.rfile = io.BytesIO(body)
    h.wfile = io.BytesIO()
    h._status = None
    h.send_response = lambda code, message=None: setattr(h, "_status", code)
    h.send_header = lambda *a, **k: None
    h.end_headers = lambda: None
    h.do_POST()
    return h._status, json.loads(h.wfile.getvalue().decode("utf-8"))


def b64(raw):
    return base64.b64encode(raw).decode()


def make_docx(paragraphs):
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as zf:
        body = "".join(f"<w:p><w:r><w:t>{p}</w:t></w:r></w:p>" for p in paragraphs)
        zf.writestr("word/document.xml",
                    '<?xml version="1.0"?><w:document xmlns:w="w">'
                    f"<w:body>{body}</w:body></w:document>")
    return buf.getvalue()


class TemplateTest(unittest.TestCase):
    def test_template_has_all_sections(self):
        text = persona.build_template({"name": "张骞", "era": "西汉",
                                       "role": "出使西域的使者", "stance": "主张联合大月氏"})
        self.assertEqual(persona.missing_sections(text), [])
        self.assertIn("张骞", text)
        self.assertIn("西汉", text)

    def test_template_with_empty_fields_still_valid(self):
        self.assertEqual(persona.missing_sections(persona.build_template({})), [])

    def test_missing_sections_detects_gaps(self):
        self.assertEqual(len(persona.missing_sections("只有一句话")), 4)

    def test_limit_wording_is_normalised(self):
        text = persona.build_template({"limit": ">150 字"})
        self.assertIn("每次回答控制在 >150 字", text)


class GenerateTest(unittest.TestCase):
    def test_default_mode_is_template(self):
        r = persona.generate("mock", "", "", "", {"name": "A"})
        self.assertEqual(r["mode"], "template")
        self.assertIsNone(r["note"])

    def test_ai_mode_with_mock_falls_back_to_template(self):
        r = persona.generate("mock", "", "", "", {"name": "A"}, mode="ai")
        self.assertEqual(r["mode"], "template")

    def test_ai_failure_falls_back_and_reports(self):
        with mock.patch.object(persona.providers, "chat", side_effect=RuntimeError("boom")):
            r = persona.generate("openai", "", "k", "m", {"name": "A"}, mode="ai")
        self.assertEqual(r["mode"], "template")
        self.assertIn("AI 生成失败", r["note"])
        self.assertEqual(persona.missing_sections(r["prompt"]), [])

    def test_ai_output_missing_sections_falls_back(self):
        with mock.patch.object(persona.providers, "chat", return_value="太简略了"):
            r = persona.generate("openai", "", "k", "m", {"name": "A"}, mode="ai")
        self.assertEqual(r["mode"], "template")
        self.assertIn("缺少必需章节", r["note"])


class ExtractTest(unittest.TestCase):
    def test_plain_text(self):
        self.assertEqual(documents.extract_text("a.md", b64("你好\n世界".encode())), "你好\n世界")

    def test_txt(self):
        self.assertIn("persona", documents.extract_text("a.txt", b64(b"persona text")))

    def test_docx_paragraphs_become_lines(self):
        text = documents.extract_text("a.docx", b64(make_docx(["第一段", "第二段"])))
        self.assertEqual(text, "第一段\n第二段")

    def test_unsupported_extension(self):
        with self.assertRaises(documents.ExtractError) as ctx:
            documents.extract_text("a.pdf", b64(b"%PDF-1.4"))
        self.assertEqual(ctx.exception.args[0], "unsupported_type")

    def test_bad_base64(self):
        with self.assertRaises(documents.ExtractError) as ctx:
            documents.extract_text("a.txt", "!!!!")
        self.assertEqual(ctx.exception.args[0], "bad_data")

    def test_too_large_rejected_before_decoding(self):
        huge = "A" * (documents.MAX_BYTES * 4 // 3 + 5000)
        with self.assertRaises(documents.ExtractError) as ctx:
            documents.extract_text("a.txt", huge)
        self.assertEqual(ctx.exception.args[0], "too_large")

    def test_broken_docx(self):
        with self.assertRaises(documents.ExtractError) as ctx:
            documents.extract_text("a.docx", b64(b"not a zip"))
        self.assertEqual(ctx.exception.args[0], "bad_data")

    def test_truncated_to_max_chars(self):
        long_text = "字" * (documents.MAX_CHARS + 500)
        self.assertEqual(len(documents.extract_text("a.txt", b64(long_text.encode()))),
                         documents.MAX_CHARS)


class RouteTest(unittest.TestCase):
    def test_persona_route(self):
        status, body = post("/api/persona", {"fields": {"name": "林肯"}, "mode": "template"})
        self.assertEqual(status, 200)
        self.assertEqual(body["mode"], "template")
        self.assertIn("林肯", body["prompt"])
        self.assertEqual(persona.missing_sections(body["prompt"]), [])

    def test_extract_route(self):
        status, body = post("/api/extract", {"filename": "p.md", "data": b64("# 人物设定".encode())})
        self.assertEqual(status, 200)
        self.assertIn("人物设定", body["text"])

    def test_extract_route_rejects_pdf(self):
        status, body = post("/api/extract", {"filename": "p.pdf", "data": b64(b"x")})
        self.assertEqual(status, 400)
        self.assertEqual(body["code"], "unsupported_type")


if __name__ == "__main__":
    unittest.main()
