# -*- coding: utf-8 -*-
"""LLM 接口适配：把不同厂商的 API 统一成一次 chat 调用。

密钥只随请求从浏览器传来，不在服务端落盘（遵循 AGENTS.md §8）。
"""
import json
import os
import ssl
import urllib.error
import urllib.request

PROVIDERS = [
    {
        "id": "mock",
        "label": "离线演示（无需 API）",
        "kind": "mock",
        "default_base_url": "",
        "default_model": "demo",
        "need_key": False,
    },
    {
        "id": "openai",
        "label": "OpenAI 兼容（OpenAI / DeepSeek / 通义 / 智谱 …）",
        "kind": "openai",
        "default_base_url": "https://api.openai.com/v1",
        "default_model": "gpt-4o-mini",
        "need_key": True,
    },
    {
        "id": "ollama",
        "label": "本地 Ollama",
        "kind": "openai",
        "default_base_url": "http://localhost:11434/v1",
        "default_model": "qwen2.5:7b",
        "need_key": False,
    },
    {
        "id": "anthropic",
        "label": "Anthropic Claude",
        "kind": "anthropic",
        "default_base_url": "https://api.anthropic.com",
        "default_model": "claude-3-5-sonnet-latest",
        "need_key": True,
    },
]

PUBLIC_PROVIDERS = [
    {k: p[k] for k in ("id", "label", "default_base_url", "default_model", "need_key")}
    for p in PROVIDERS
]

# macOS 上 python.org 版 Python 常常没有根证书（默认 cafile 为空），
# 这里主动挑选一个可用的 CA 包，避免 SSL: CERTIFICATE_VERIFY_FAILED。
_CA_CANDIDATES = (
    "/etc/ssl/cert.pem",                                  # macOS 系统证书包
    "/etc/ssl/certs/ca-certificates.crt",                 # Debian/Ubuntu
    "/etc/pki/tls/certs/ca-bundle.crt",                   # RHEL/CentOS
    "/usr/local/etc/openssl@3/cert.pem",                  # Intel Homebrew
    "/opt/homebrew/etc/openssl@3/cert.pem",               # Apple Silicon Homebrew
)


def _ssl_context():
    env_path = os.environ.get("SSL_CERT_FILE")
    if env_path and os.path.exists(env_path):
        return ssl.create_default_context(cafile=env_path)
    try:  # 若装了 certifi，优先用它
        import certifi  # noqa: PLC0415

        return ssl.create_default_context(cafile=certifi.where())
    except Exception:
        pass
    for path in _CA_CANDIDATES:
        if os.path.exists(path):
            try:
                return ssl.create_default_context(cafile=path)
            except Exception:
                continue
    return ssl.create_default_context()


def _normalize_base(base_url, default):
    base = (base_url or default or "").strip().rstrip("/")
    if base and not base.startswith(("http://", "https://")):
        raise ValueError(
            f"Base URL 必须以 http:// 或 https:// 开头（当前填的是「{base}」）。"
            "例如 DeepSeek 填 https://api.deepseek.com"
        )
    return base


def _post_json(url, payload, headers, timeout=60):
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers=headers, method="POST")
    try:
        with urllib.request.urlopen(  # noqa: S310
            req, timeout=timeout, context=_ssl_context()
        ) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", "replace")
        raise RuntimeError(f"接口返回 HTTP {exc.code}：{detail[:400]}") from exc
    except urllib.error.URLError as exc:
        reason = getattr(exc, "reason", exc)
        raise RuntimeError(f"无法连接 {url}：{reason}") from exc
    except TimeoutError as exc:
        raise RuntimeError(f"连接 {url} 超时") from exc


def chat(provider_id, base_url, api_key, model, system, messages, figure_name="", temperature=0.8):
    spec = next((p for p in PROVIDERS if p["id"] == provider_id), None)
    if spec is None:
        raise ValueError(f"未知 API 接口：{provider_id}")

    kind = spec["kind"]
    if kind == "mock":
        last = messages[-1]["content"] if messages else "……"
        name = figure_name or "历史人物"
        return (
            f"（离线演示模式）我是{name}。你问：「{last}」。\n"
            "当前未接入真实模型，这是一条模拟回复。"
            "请在对话框下方选择 API 接口、填入密钥后重试。"
        )

    base = _normalize_base(base_url, spec["default_base_url"])
    model = model or spec["default_model"]
    if not base:
        raise ValueError("请填写 Base URL")

    if kind == "openai":
        payload = {
            "model": model,
            "messages": [{"role": "system", "content": system}, *messages],
            "temperature": temperature,
        }
        headers = {"Content-Type": "application/json"}
        if api_key:
            headers["Authorization"] = f"Bearer {api_key}"
        data = _post_json(f"{base}/chat/completions", payload, headers)
        try:
            return (data["choices"][0]["message"]["content"] or "").strip()
        except (KeyError, IndexError) as exc:
            raise RuntimeError(f"接口返回格式异常：{json.dumps(data, ensure_ascii=False)[:300]}") from exc

    if kind == "anthropic":
        payload = {"model": model, "max_tokens": 800, "temperature": temperature,
                   "system": system, "messages": messages}
        headers = {
            "Content-Type": "application/json",
            "x-api-key": api_key or "",
            "anthropic-version": "2023-06-01",
        }
        data = _post_json(f"{base}/v1/messages", payload, headers)
        return "".join(b.get("text", "") for b in data.get("content", [])).strip()

    raise ValueError(f"未实现的接口类型：{kind}")
