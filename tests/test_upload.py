# -*- coding: utf-8 -*-
"""形象上传接口测试（P0-6）。"""
import base64
import io
import json
import tempfile
import unittest
from pathlib import Path

from src.app import server, uploads

# 1x1 透明 PNG
PNG_B64 = ("iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8"
           "BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg==")


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


class UploadTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self._orig = uploads.UPLOAD_DIR
        uploads.UPLOAD_DIR = Path(self.tmp.name) / "uploads"

    def tearDown(self):
        uploads.UPLOAD_DIR = self._orig
        self.tmp.cleanup()

    def test_valid_png_is_saved(self):
        status, body = post("/api/upload", {"filename": "hero.png", "data": PNG_B64})
        self.assertEqual(status, 200)
        rel = body["path"]
        self.assertTrue(rel.startswith("assets/avatars/uploads/"))
        self.assertTrue(rel.endswith(".png"))
        saved = list(uploads.UPLOAD_DIR.glob("*.png"))
        self.assertEqual(len(saved), 1)
        self.assertEqual(saved[0].read_bytes(), base64.b64decode(PNG_B64))

    def test_data_url_prefix_is_accepted(self):
        status, _ = post("/api/upload",
                         {"filename": "a.jpg", "data": f"data:image/jpeg;base64,{PNG_B64}"})
        self.assertEqual(status, 200)

    def test_svg_is_rejected(self):
        status, body = post("/api/upload", {"filename": "evil.svg", "data": PNG_B64})
        self.assertEqual(status, 400)
        self.assertEqual(body["code"], "unsupported_type")
        self.assertFalse(uploads.UPLOAD_DIR.exists() and list(uploads.UPLOAD_DIR.iterdir()))

    def test_txt_is_rejected(self):
        status, body = post("/api/upload", {"filename": "a.txt", "data": PNG_B64})
        self.assertEqual(status, 400)
        self.assertEqual(body["code"], "unsupported_type")

    def test_oversized_is_rejected_before_decoding(self):
        huge = "A" * (uploads.MAX_BYTES * 4 // 3 + 5000)
        status, body = post("/api/upload", {"filename": "big.png", "data": huge})
        self.assertEqual(status, 400)
        self.assertEqual(body["code"], "too_large")

    def test_invalid_base64_is_rejected(self):
        status, body = post("/api/upload", {"filename": "a.png", "data": "这不是base64!!"})
        self.assertEqual(status, 400)
        self.assertEqual(body["code"], "bad_data")

    def test_missing_filename_is_rejected(self):
        status, body = post("/api/upload", {"filename": "", "data": PNG_B64})
        self.assertEqual(status, 400)
        self.assertEqual(body["code"], "unsupported_type")


class UploadDefaultsTest(unittest.TestCase):
    """默认配置检查（不打补丁，验证真实目录）。"""

    def test_default_dir_sits_under_web_so_static_handler_serves_it(self):
        self.assertTrue(str(uploads.UPLOAD_DIR).startswith(str(uploads.WEB)))
        self.assertTrue(uploads.URL_PREFIX.startswith("assets/"))
        self.assertNotIn("svg", uploads.ALLOWED)

    def test_limits(self):
        self.assertEqual(uploads.MAX_BYTES, 2 * 1024 * 1024)


if __name__ == "__main__":
    unittest.main()
