from __future__ import annotations

import json
import os
import sys
import threading
import time
import urllib.error
import urllib.request
from typing import Any

from .config import load_llm_config

_verbose = False


def _log(msg: str) -> None:
    if _verbose:
        print(f"[llm] {msg}", file=sys.stderr)


PROVIDERS: dict[str, str] = {
    "ollama": "http://localhost:11434/v1/chat/completions",
    "vllm": "http://localhost:8000/v1/chat/completions",
    "lmstudio": "http://localhost:1234/v1/chat/completions",
}


class LLMError(Exception):
    pass


def _coerce_param(key: str, value: str) -> int | float | str:
    int_keys = {"max_tokens", "n", "seed", "top_k"}
    float_keys = {"temperature", "top_p", "frequency_penalty", "presence_penalty"}
    if key in int_keys:
        try:
            return int(value)
        except ValueError:
            raise LLMError(f"Expected integer for {key}, got: {value}")
    if key in float_keys:
        try:
            return float(value)
        except ValueError:
            raise LLMError(f"Expected number for {key}, got: {value}")
    return value


def resolve_target(
    llm_flag: str | bool | None,
    target_name: str | None,
    model: str | None,
    system_prompt: str | None,
    api_key: str | None,
    set_params: list[str] | None,
) -> dict[str, Any]:
    target_cfg: dict[str, Any] = {}

    # Load target from config if requested
    if target_name is not None or llm_flag is True:
        llm_config = load_llm_config()
        if target_name is None:
            target_name = llm_config.get("default_target")
            if target_name is None:
                raise LLMError("No --llm value and no default_target in config")

        _log(f"Loading target '{target_name}' from config")
        targets = llm_config.get("targets", {})
        if target_name not in targets:
            raise LLMError(f"LLM target '{target_name}' not found in config")
        target_cfg = dict(targets[target_name])

    # Resolve URL
    url = target_cfg.get("url")
    provider = target_cfg.get("provider")

    if isinstance(llm_flag, str):
        if llm_flag in PROVIDERS:
            url = PROVIDERS[llm_flag]
            provider = llm_flag
        elif llm_flag.startswith("http://") or llm_flag.startswith("https://"):
            url = llm_flag
        else:
            raise LLMError(
                f"Unknown provider '{llm_flag}'. Use: ollama, vllm, lmstudio or a URL"
            )
    elif provider and not url:
        if provider in PROVIDERS:
            url = PROVIDERS[provider]
        else:
            raise LLMError(
                f"Unknown provider '{provider}'. Use: ollama, vllm, lmstudio or a URL"
            )

    if not url:
        raise LLMError(
            "No URL could be resolved. Use --llm <provider|url> or configure a target"
        )

    # Resolve model
    resolved_model = model or target_cfg.get("model")
    if not resolved_model:
        raise LLMError("No model specified. Use --model or set model in target config")

    # Resolve system prompt
    resolved_system_prompt = system_prompt or target_cfg.get("system_prompt")

    # Resolve API key
    resolved_api_key = api_key
    if not resolved_api_key:
        api_key_env = target_cfg.get("api_key_env")
        if api_key_env:
            resolved_api_key = os.environ.get(api_key_env)
            if not resolved_api_key:
                raise LLMError(f"Environment variable '{api_key_env}' not set")

    # Resolve extra params from config
    params: dict[str, Any] = {}
    for k in ("temperature", "top_p", "max_tokens", "n", "seed", "top_k",
              "frequency_penalty", "presence_penalty"):
        if k in target_cfg:
            params[k] = target_cfg[k]

    # Override with --set params
    if set_params:
        for item in set_params:
            if "=" not in item:
                raise LLMError(f"--set value must be KEY=VALUE, got: {item}")
            k, v = item.split("=", 1)
            params[k] = _coerce_param(k, v)

    _log(f"URL: {url}")
    _log(f"Model: {resolved_model}")
    if resolved_system_prompt:
        _log(f"System prompt: {resolved_system_prompt[:80]}{'...' if len(resolved_system_prompt) > 80 else ''}")
    if resolved_api_key:
        _log("API key: ***")
    if params:
        _log(f"Params: {params}")

    return {
        "url": url,
        "model": resolved_model,
        "system_prompt": resolved_system_prompt,
        "api_key": resolved_api_key,
        "params": params,
    }


def build_payload(
    model: str,
    user_content: str,
    system_prompt: str | None = None,
    params: dict[str, Any] | None = None,
) -> dict[str, Any]:
    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": user_content})

    payload: dict[str, Any] = {"model": model, "messages": messages}
    if params:
        payload.update(params)
    return payload


def send_request(target: dict[str, Any], user_content: str) -> dict[str, Any]:
    url = target["url"]
    payload = build_payload(
        model=target["model"],
        user_content=user_content,
        system_prompt=target.get("system_prompt"),
        params=target.get("params"),
    )

    data = json.dumps(payload).encode("utf-8")
    headers = {"Content-Type": "application/json"}
    if target.get("api_key"):
        headers["Authorization"] = f"Bearer {target['api_key']}"

    _log(f"Sending {len(data)} bytes to {url}")
    req = urllib.request.Request(url, data=data, headers=headers, method="POST")

    try:
        with urllib.request.urlopen(req, timeout=240) as resp:
            body = json.loads(resp.read().decode("utf-8"))
            _log(f"Response received (usage: {body.get('usage', 'n/a')})")
    except urllib.error.HTTPError as e:
        body_text = ""
        try:
            body_text = e.read().decode("utf-8", errors="replace")
        except Exception:
            pass
        raise LLMError(f"HTTP {e.code} from {url}: {body_text}")
    except urllib.error.URLError as e:
        reason = str(e.reason) if hasattr(e, "reason") else str(e)
        if "Connection refused" in reason:
            raise LLMError(f"Could not connect to {url}: Connection refused")
        raise LLMError(f"Could not connect to {url}: {reason}")
    except TimeoutError:
        raise LLMError(f"Request to {url} timed out after 240s")

    try:
        content = body["choices"][0]["message"]["content"]
    except (KeyError, IndexError, TypeError):
        raise LLMError(f"Unexpected response format from {url}")

    usage = body.get("usage", {})
    return {"content": content, "usage": usage}


def handle_llm(args, output: str) -> str:
    """Entry point called from core.py. Returns the LLM response text."""
    global _verbose
    _verbose = getattr(args, "verbose", False)

    target = resolve_target(
        llm_flag=args.llm,
        target_name=args.target,
        model=args.model,
        system_prompt=args.system_prompt,
        api_key=args.api_key,
        set_params=args.set,
    )

    target_name = args.target or "default"
    est_tokens = len(output) // 4
    GREEN = "\033[92m"
    RESET = "\033[0m"
    print(f"[llm] target: {target_name} | model: {target['model']} | ~{est_tokens} tokens", file=sys.stderr)

    stop_event = threading.Event()

    def _spinner():
        start = time.monotonic()
        while not stop_event.is_set():
            elapsed = time.monotonic() - start
            sys.stderr.write(f"\r{GREEN}[llm] waiting... {elapsed:.1f}s{RESET}")
            sys.stderr.flush()
            stop_event.wait(0.1)
        elapsed = time.monotonic() - start
        sys.stderr.write(f"\r{GREEN}[llm] completed in {elapsed:.1f}s{RESET}\n")
        sys.stderr.flush()

    t = threading.Thread(target=_spinner, daemon=True)
    t.start()
    try:
        result = send_request(target, output)
    finally:
        stop_event.set()
        t.join()

    return result["content"]
