# Configuration

Dumpcat supports project-level configuration via `.dumpcat.toml` files. This lets you define defaults and named profiles so you don't have to repeat flags.

## Config file discovery

Dumpcat looks for configuration in this order:

1. **Explicit path** — `--config path/to/config.toml`
2. **Walk up** — `.dumpcat.toml` in the target directory, then each parent directory
3. **Global** — `~/.config/dumpcat/config.toml`

The first file found is used. If no config is found, built-in defaults apply.

## File format

```toml
[default]
format = "markdown"
gitignore = true
max_size = "1mb"
hidden = false
exclude = ["__pycache__", ".git", "*.pyc", "*.lock"]

[profiles.python]
include = [".py", ".pyi", ".toml", ".cfg", ".txt", ".md"]
exclude = ["__pycache__", ".git", "*.pyc", ".venv", ".mypy_cache"]

[profiles.web]
include = [".js", ".ts", ".jsx", ".tsx", ".css", ".html", ".json"]
exclude = ["node_modules", "dist", "build", ".next"]
```

## Sections

### `[default]`

Base settings applied to every run. Supports the same keys as profile sections.

### `[profiles.<name>]`

Named profiles that layer on top of `[default]`. Activate with `--profile`:

```bash
dumpcat --profile python
```

## Supported keys

| Key | Type | Description |
|---|---|---|
| `format` | string | `"markdown"`, `"plain"`, or `"json"` |
| `include` | list of strings | File extensions to include |
| `exclude` | list of strings | Glob patterns to exclude |
| `depth` | integer | Max directory depth |
| `max_size` | string | Max file size (e.g. `"500kb"`) |
| `hidden` | boolean | Include dotfiles/dotdirs |

## Precedence

Settings are merged in this order (later wins):

```
built-in defaults < [default] section < [profiles.X] section < CLI flags
```

CLI flags always take priority. This means you can set sensible defaults in your config and override them on a per-command basis.

## Example workflow

Create a `.dumpcat.toml` in your project root:

```toml
[default]
exclude = ["__pycache__", "*.pyc", ".venv", "node_modules"]

[profiles.backend]
include = [".py", ".sql", ".toml"]
exclude = ["__pycache__", "*.pyc", ".venv", "migrations"]

[profiles.frontend]
include = [".ts", ".tsx", ".css", ".html"]
exclude = ["node_modules", "dist", ".next"]
```

Then use it:

```bash
# Uses [default] settings
dumpcat

# Uses [profiles.backend] layered on [default]
dumpcat --profile backend

# Override depth even with a profile
dumpcat --profile backend -d 3
```

Commit the `.dumpcat.toml` to your repo so your team shares the same profiles.

## LLM configuration

LLM targets are configured in a separate file: `~/.dumpcat/dumpcat_profiles.toml`. Run `dumpcat init` to create a starter config.

### Config file format

```toml
[llm]
default_target = "ollama"

[llm.targets.ollama]
provider = "ollama"
model = "llama3"
system_prompt = "You are a helpful coding assistant."
temperature = 0.7
max_tokens = 4096

[llm.targets.openai]
url = "https://api.openai.com/v1/chat/completions"
model = "gpt-4o"
api_key_env = "OPENAI_API_KEY"
temperature = 0.7
```

### Target keys

| Key | Type | Description |
|---|---|---|
| `provider` | string | Built-in provider: `ollama`, `vllm`, or `lmstudio` |
| `url` | string | Full endpoint URL (overrides `provider`) |
| `model` | string | Model name |
| `system_prompt` | string | Default system prompt |
| `api_key_env` | string | Environment variable containing the API key |
| `temperature` | float | Sampling temperature |
| `top_p` | float | Top-p sampling |
| `max_tokens` | integer | Maximum response tokens |
| `n` | integer | Number of completions |
| `seed` | integer | Random seed |
| `top_k` | integer | Top-k sampling |
| `frequency_penalty` | float | Frequency penalty |
| `presence_penalty` | float | Presence penalty |

### Usage

```bash
# Use the default target
dumpcat --llm -p "Review this code"

# Use a named target
dumpcat --llm -t openai -p "Review this code"

# Override model from a target
dumpcat --llm -t ollama -m mistral

# CLI flags override target config
dumpcat --llm -t openai --set temperature=0 --system-prompt "Be brief"
```

### Precedence

LLM settings are resolved in this order (later wins):

```
target config < CLI flags (--model, --system-prompt, --set, --api-key)
```
