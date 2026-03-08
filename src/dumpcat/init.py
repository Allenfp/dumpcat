from __future__ import annotations

import sys
from pathlib import Path

TEMPLATE = """\
# dumpcat LLM profiles
# Run `dumpcat --help` for CLI usage

# ─── LLM targets ────────────────────────────────────────
[llm]
default_target = "ollama"

[llm.targets.ollama]
provider = "ollama"
# model = ""  # Required: set your model name (e.g. "llama3")
# system_prompt = "You are a helpful coding assistant."
# temperature = 0.7
# top_p = 0.9
# max_tokens = 4096

[llm.targets.vllm]
provider = "vllm"
# model = ""  # Required: set your model name (e.g. "mistral")
# system_prompt = "You are a helpful coding assistant."
# temperature = 0.7
# top_p = 0.9
# max_tokens = 4096

[llm.targets.lmstudio]
provider = "lmstudio"
# model = ""  # Required: set your model name (e.g. "codellama")
# system_prompt = "You are a helpful coding assistant."
# temperature = 0.7
# top_p = 0.9
# max_tokens = 4096

# ─── Cloud example (OpenAI) ─────────────────────────────
# [llm.targets.openai]
# url = "https://api.openai.com/v1/chat/completions"
# model = ""  # Required: set your model name (e.g. "gpt-4o")
# api_key_env = "OPENAI_API_KEY"
# system_prompt = "You are a helpful coding assistant."
# temperature = 0.7
# top_p = 0.9
# max_tokens = 4096
"""

CONFIG_DIR = Path.home() / ".dumpcat"
CONFIG_FILE = CONFIG_DIR / "dumpcat_profiles.toml"


def run_init(argv: list[str]) -> None:
    force = "--force" in argv

    if CONFIG_FILE.exists() and not force:
        print(
            f"Config already exists: {CONFIG_FILE}. Use --force to overwrite.",
            file=sys.stderr,
        )
        sys.exit(1)

    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    CONFIG_FILE.write_text(TEMPLATE, encoding="utf-8")
    print(f"Created {CONFIG_FILE}", file=sys.stderr)
