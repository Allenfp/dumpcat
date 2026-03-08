import json
import types
from unittest.mock import MagicMock

import pytest

from dumpcat.llm import (
    LLMError,
    PROVIDERS,
    _coerce_param,
    build_payload,
    handle_llm,
    resolve_target,
    send_request,
)


# ── _coerce_param ──────────────────────────────────────

def test_coerce_int():
    assert _coerce_param("max_tokens", "4096") == 4096


def test_coerce_float():
    assert _coerce_param("temperature", "0.7") == 0.7


def test_coerce_string():
    assert _coerce_param("stop", "###") == "###"


def test_coerce_int_bad():
    with pytest.raises(LLMError, match="Expected integer"):
        _coerce_param("max_tokens", "abc")


def test_coerce_float_bad():
    with pytest.raises(LLMError, match="Expected number"):
        _coerce_param("temperature", "abc")


# ── build_payload ──────────────────────────────────────

def test_build_payload_basic():
    p = build_payload("llama3", "hello")
    assert p["model"] == "llama3"
    assert len(p["messages"]) == 1
    assert p["messages"][0] == {"role": "user", "content": "hello"}


def test_build_payload_with_system():
    p = build_payload("llama3", "hello", system_prompt="Be helpful")
    assert len(p["messages"]) == 2
    assert p["messages"][0] == {"role": "system", "content": "Be helpful"}


def test_build_payload_with_params():
    p = build_payload("llama3", "hello", params={"temperature": 0.5})
    assert p["temperature"] == 0.5


# ── resolve_target ─────────────────────────────────────

def test_resolve_with_provider():
    t = resolve_target("ollama", None, "llama3", None, None, None)
    assert t["url"] == PROVIDERS["ollama"]
    assert t["model"] == "llama3"


def test_resolve_with_url():
    url = "http://myserver:8080/v1/chat/completions"
    t = resolve_target(url, None, "gpt-4", None, None, None)
    assert t["url"] == url
    assert t["model"] == "gpt-4"


def test_resolve_unknown_provider():
    with pytest.raises(LLMError, match="Unknown provider 'badname'"):
        resolve_target("badname", None, "model", None, None, None)


def test_resolve_no_model():
    with pytest.raises(LLMError, match="No model specified"):
        resolve_target("ollama", None, None, None, None, None)


def test_resolve_set_params():
    t = resolve_target("ollama", None, "llama3", None, None, ["temperature=0.9", "max_tokens=100"])
    assert t["params"]["temperature"] == 0.9
    assert t["params"]["max_tokens"] == 100


def test_resolve_bad_set_format():
    with pytest.raises(LLMError, match="--set value must be KEY=VALUE"):
        resolve_target("ollama", None, "llama3", None, None, ["bad"])


def test_resolve_system_prompt():
    t = resolve_target("ollama", None, "llama3", "Review code", None, None)
    assert t["system_prompt"] == "Review code"


def test_resolve_api_key():
    t = resolve_target("ollama", None, "llama3", None, "sk-123", None)
    assert t["api_key"] == "sk-123"


def test_resolve_from_target_config(monkeypatch):
    fake_config = {
        "default_target": "mylocal",
        "targets": {
            "mylocal": {
                "provider": "ollama",
                "model": "mistral",
                "temperature": 0.5,
            }
        },
    }
    monkeypatch.setattr("dumpcat.llm.load_llm_config", lambda: fake_config)
    t = resolve_target(True, None, None, None, None, None)
    assert t["url"] == PROVIDERS["ollama"]
    assert t["model"] == "mistral"
    assert t["params"]["temperature"] == 0.5


def test_resolve_target_not_found(monkeypatch):
    monkeypatch.setattr("dumpcat.llm.load_llm_config", lambda: {"targets": {}})
    with pytest.raises(LLMError, match="not found in config"):
        resolve_target(True, "missing", None, None, None, None)


def test_resolve_no_default_target(monkeypatch):
    monkeypatch.setattr("dumpcat.llm.load_llm_config", lambda: {})
    with pytest.raises(LLMError, match="No --llm value and no default_target"):
        resolve_target(True, None, None, None, None, None)


def test_resolve_target_no_model_in_config(monkeypatch):
    fake_config = {
        "default_target": "ollama",
        "targets": {
            "ollama": {"provider": "ollama"},
        },
    }
    monkeypatch.setattr("dumpcat.llm.load_llm_config", lambda: fake_config)
    with pytest.raises(LLMError, match="No model specified"):
        resolve_target(True, None, None, None, None, None)


def test_resolve_api_key_from_env(monkeypatch):
    fake_config = {
        "default_target": "cloud",
        "targets": {
            "cloud": {
                "url": "https://api.example.com/v1/chat/completions",
                "model": "gpt-4o",
                "api_key_env": "MY_API_KEY",
            }
        },
    }
    monkeypatch.setattr("dumpcat.llm.load_llm_config", lambda: fake_config)
    monkeypatch.setenv("MY_API_KEY", "secret-123")
    t = resolve_target(True, "cloud", None, None, None, None)
    assert t["api_key"] == "secret-123"


def test_resolve_api_key_env_missing(monkeypatch):
    fake_config = {
        "default_target": "cloud",
        "targets": {
            "cloud": {
                "url": "https://api.example.com/v1/chat/completions",
                "model": "gpt-4o",
                "api_key_env": "MISSING_KEY",
            }
        },
    }
    monkeypatch.setattr("dumpcat.llm.load_llm_config", lambda: fake_config)
    monkeypatch.delenv("MISSING_KEY", raising=False)
    with pytest.raises(LLMError, match="Environment variable 'MISSING_KEY' not set"):
        resolve_target(True, "cloud", None, None, None, None)


def test_resolve_cli_overrides_target(monkeypatch):
    fake_config = {
        "targets": {
            "local": {
                "provider": "ollama",
                "model": "llama3",
                "temperature": 0.5,
            }
        },
    }
    monkeypatch.setattr("dumpcat.llm.load_llm_config", lambda: fake_config)
    t = resolve_target("vllm", "local", "mistral", "Be brief", "key123", ["temperature=0.9"])
    assert t["url"] == PROVIDERS["vllm"]
    assert t["model"] == "mistral"
    assert t["system_prompt"] == "Be brief"
    assert t["api_key"] == "key123"
    assert t["params"]["temperature"] == 0.9


# ── send_request ───────────────────────────────────────

def test_send_request_success(monkeypatch):
    response_body = json.dumps({
        "choices": [{"message": {"content": "Here is my review."}}]
    }).encode()

    mock_resp = MagicMock()
    mock_resp.read.return_value = response_body
    mock_resp.__enter__ = lambda s: s
    mock_resp.__exit__ = MagicMock(return_value=False)

    monkeypatch.setattr("urllib.request.urlopen", lambda req, timeout=None: mock_resp)

    target = {
        "url": "http://localhost:11434/v1/chat/completions",
        "model": "llama3",
        "system_prompt": None,
        "api_key": None,
        "params": {},
    }
    result = send_request(target, "hello")
    assert result == {"content": "Here is my review.", "usage": {}}


def test_send_request_bad_json_response(monkeypatch):
    mock_resp = MagicMock()
    mock_resp.read.return_value = json.dumps({"bad": "format"}).encode()
    mock_resp.__enter__ = lambda s: s
    mock_resp.__exit__ = MagicMock(return_value=False)

    monkeypatch.setattr("urllib.request.urlopen", lambda req, timeout=None: mock_resp)

    target = {
        "url": "http://localhost:11434/v1/chat/completions",
        "model": "llama3",
        "system_prompt": None,
        "api_key": None,
        "params": {},
    }
    with pytest.raises(LLMError, match="Unexpected response format"):
        send_request(target, "hello")


def test_send_request_http_error(monkeypatch):
    import urllib.error

    def raise_http_error(req, timeout=None):
        raise urllib.error.HTTPError(
            url=req.full_url, code=401, msg="Unauthorized",
            hdrs={}, fp=MagicMock(read=lambda: b"bad key"),
        )

    monkeypatch.setattr("urllib.request.urlopen", raise_http_error)

    target = {
        "url": "http://localhost:11434/v1/chat/completions",
        "model": "llama3",
        "system_prompt": None,
        "api_key": None,
        "params": {},
    }
    with pytest.raises(LLMError, match="HTTP 401"):
        send_request(target, "hello")


def test_send_request_connection_refused(monkeypatch):
    import urllib.error

    def raise_url_error(req, timeout=None):
        raise urllib.error.URLError("Connection refused")

    monkeypatch.setattr("urllib.request.urlopen", raise_url_error)

    target = {
        "url": "http://localhost:11434/v1/chat/completions",
        "model": "llama3",
        "system_prompt": None,
        "api_key": None,
        "params": {},
    }
    with pytest.raises(LLMError, match="Connection refused"):
        send_request(target, "hello")


def test_send_request_timeout(monkeypatch):
    def raise_timeout(req, timeout=None):
        raise TimeoutError()

    monkeypatch.setattr("urllib.request.urlopen", raise_timeout)

    target = {
        "url": "http://localhost:11434/v1/chat/completions",
        "model": "llama3",
        "system_prompt": None,
        "api_key": None,
        "params": {},
    }
    with pytest.raises(LLMError, match="timed out"):
        send_request(target, "hello")


def test_send_request_includes_auth_header(monkeypatch):
    captured_req = {}

    response_body = json.dumps({
        "choices": [{"message": {"content": "ok"}}]
    }).encode()

    mock_resp = MagicMock()
    mock_resp.read.return_value = response_body
    mock_resp.__enter__ = lambda s: s
    mock_resp.__exit__ = MagicMock(return_value=False)

    def capture_urlopen(req, timeout=None):
        captured_req["headers"] = dict(req.headers)
        return mock_resp

    monkeypatch.setattr("urllib.request.urlopen", capture_urlopen)

    target = {
        "url": "http://localhost:11434/v1/chat/completions",
        "model": "llama3",
        "system_prompt": None,
        "api_key": "sk-test",
        "params": {},
    }
    send_request(target, "hello")
    assert captured_req["headers"]["Authorization"] == "Bearer sk-test"


# ── handle_llm (integration with args) ────────────────

def test_handle_llm(monkeypatch):
    response_body = json.dumps({
        "choices": [{"message": {"content": "response text"}}]
    }).encode()

    mock_resp = MagicMock()
    mock_resp.read.return_value = response_body
    mock_resp.__enter__ = lambda s: s
    mock_resp.__exit__ = MagicMock(return_value=False)

    monkeypatch.setattr("urllib.request.urlopen", lambda req, timeout=None: mock_resp)

    args = types.SimpleNamespace(
        llm="ollama", target=None, model="llama3",
        system_prompt=None, api_key=None, set=None, verbose=False,
    )
    result = handle_llm(args, "dump content here")
    assert result == "response text"


def test_handle_llm_verbose(monkeypatch, capsys):
    response_body = json.dumps({
        "choices": [{"message": {"content": "ok"}}]
    }).encode()

    mock_resp = MagicMock()
    mock_resp.read.return_value = response_body
    mock_resp.__enter__ = lambda s: s
    mock_resp.__exit__ = MagicMock(return_value=False)

    monkeypatch.setattr("urllib.request.urlopen", lambda req, timeout=None: mock_resp)

    args = types.SimpleNamespace(
        llm="ollama", target=None, model="llama3",
        system_prompt="Be helpful", api_key="sk-x", set=["temperature=0.5"],
        verbose=True,
    )
    handle_llm(args, "hello")
    captured = capsys.readouterr()
    assert "[llm] URL:" in captured.err
    assert "[llm] Model: llama3" in captured.err
    assert "[llm] System prompt: Be helpful" in captured.err
    assert "[llm] API key: ***" in captured.err
    assert "[llm] Params:" in captured.err
    assert "[llm] Sending" in captured.err
    assert "[llm] Response received" in captured.err


def test_verbose_not_shown_by_default(monkeypatch, capsys):
    response_body = json.dumps({
        "choices": [{"message": {"content": "ok"}}]
    }).encode()

    mock_resp = MagicMock()
    mock_resp.read.return_value = response_body
    mock_resp.__enter__ = lambda s: s
    mock_resp.__exit__ = MagicMock(return_value=False)

    monkeypatch.setattr("urllib.request.urlopen", lambda req, timeout=None: mock_resp)

    args = types.SimpleNamespace(
        llm="ollama", target=None, model="llama3",
        system_prompt=None, api_key=None, set=None, verbose=False,
    )
    handle_llm(args, "hello")
    captured = capsys.readouterr()
    # Status/spinner lines are always shown; verbose controls detailed debug output
    assert "[llm] URL:" not in captured.err
    assert "[llm] Model:" not in captured.err
