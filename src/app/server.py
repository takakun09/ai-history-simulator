# -*- coding: utf-8 -*-
"""零依赖 HTTP 服务：静态前端 + 人物 CRUD + 对话代理。

运行： python3 -m src.app.server
"""
import json
import mimetypes
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

from . import providers, store

ROOT = Path(__file__).resolve().parents[2]
WEB = ROOT / "web"
mimetypes.add_type("image/svg+xml", ".svg")
mimetypes.add_type("text/javascript", ".js")

ROUTES = {"/": "index.html", "/chat": "chat.html", "/teacher": "teacher.html"}


class Handler(BaseHTTPRequestHandler):
    server_version = "HistorySim/0.1"

    def log_message(self, *args):  # 静默访问日志
        pass

    # ---------- helpers ----------
    def _json(self, obj, status=200):
        body = json.dumps(obj, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _read_body(self):
        length = int(self.headers.get("Content-Length") or 0)
        raw = self.rfile.read(length) if length else b"{}"
        return json.loads(raw.decode("utf-8") or "{}")

    def _send_file(self, rel):
        path = (WEB / rel).resolve()
        if not str(path).startswith(str(WEB)) or not path.is_file():
            self._json({"error": "not found"}, 404)
            return
        ctype = mimetypes.guess_type(str(path))[0] or "application/octet-stream"
        data = path.read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", f"{ctype}; charset=utf-8" if ctype.startswith("text") or ctype == "image/svg+xml" else ctype)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    # ---------- GET ----------
    def do_GET(self):
        parsed = urlparse(self.path)
        path, query = parsed.path, parse_qs(parsed.query)

        if path == "/api/providers":
            return self._json({"providers": providers.PUBLIC_PROVIDERS})
        if path == "/api/figures":
            scope = (query.get("scope") or ["student"])[0]
            return self._json({"figures": store.list_figures(published_only=(scope == "student"))})
        if path.startswith("/api/figures/"):
            fig = store.get_figure(path.rsplit("/", 1)[-1])
            return self._json(fig) if fig else self._json({"error": "not found"}, 404)

        rel = ROUTES.get(path) or path.lstrip("/")
        return self._send_file(rel)

    # ---------- POST ----------
    def do_POST(self):
        path = urlparse(self.path).path
        try:
            body = self._read_body()
        except json.JSONDecodeError:
            return self._json({"error": "invalid json"}, 400)

        if path == "/api/figures":
            if not body.get("id"):
                return self._json({"error": "缺少 id"}, 400)
            return self._json({"figure": store.upsert_figure(body)})

        if path == "/api/chat":
            fig = store.get_figure(body.get("figure_id", ""))
            if not fig:
                return self._json({"error": "人物不存在"}, 404)
            messages = body.get("messages") or []
            try:
                reply = providers.chat(
                    provider_id=body.get("provider", "mock"),
                    base_url=body.get("base_url", ""),
                    api_key=body.get("api_key", ""),
                    model=body.get("model", ""),
                    system=fig.get("system_prompt", ""),
                    messages=messages,
                    figure_name=fig.get("name", ""),
                )
            except Exception as exc:  # 把上游错误回给前端，便于演示排错
                return self._json({"error": f"{type(exc).__name__}: {exc}"}, 502)
            return self._json({"reply": reply})

        return self._json({"error": "not found"}, 404)

    # ---------- DELETE ----------
    def do_DELETE(self):
        path = urlparse(self.path).path
        if path.startswith("/api/figures/"):
            ok = store.delete_figure(path.rsplit("/", 1)[-1])
            return self._json({"deleted": ok})
        return self._json({"error": "not found"}, 404)


def main(host="127.0.0.1", port=8777):
    httpd = ThreadingHTTPServer((host, port), Handler)
    print(f"AI 历史人物模拟器 Demo 运行中 → http://{host}:{port}")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n已停止。")


if __name__ == "__main__":
    main()
