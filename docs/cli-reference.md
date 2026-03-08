# CLI Reference

```
dumpcat [OPTIONS] [PATH]
```

`PATH` defaults to `.` (current directory).

## Flags

| Flag | Short | Type | Default | Description |
|---|---|---|---|---|
| `--output PATH` | `-o` | string | stdout | Write output to a file |
| `--output-append` | `-A` | flag | off | Append to output file instead of overwriting |
| `--depth INT` | `-d` | integer | unlimited | Max directory depth |
| `--include EXT` | `-i` | string (repeatable) | all files | Include only these extensions |
| `--exclude PATTERN` | `-e` | string (repeatable) | none | Exclude glob patterns |
| `--gitignore` | | flag | on | Respect `.gitignore` rules |
| `--no-gitignore` | | flag | off | Ignore `.gitignore` rules |
| `--tree-only` | | flag | off | Show only the file tree, no contents |
| `--no-tree` | | flag | off | Show only file contents, no tree |
| `--prepend TEXT` | `-p` | string | none | Text or `@filepath` to prepend |
| `--append TEXT` | `-a` | string | none | Text or `@filepath` to append |
| `--max-size SIZE` | | string | `1mb` | Skip files larger than this |
| `--stats` | `-s` | flag | off | Show file count, lines, and estimated tokens |
| `--format FORMAT` | `-f` | choice | `markdown` | Output format: `markdown`, `plain`, or `json` |
| `--config PATH` | | string | auto | Path to config file |
| `--profile NAME` | | string | `default` | Named profile from config |
| `--follow-symlinks` | | flag | off | Follow symbolic links |
| `--hidden` | | flag | off | Include dotfiles and dotdirs |
| `--line-numbers` | `-n` | flag | off | Add line numbers to file contents |
| `--version` | `-V` | | | Show version and exit |
| `--llm PROVIDER` | | string | none | Send output to an LLM (`ollama`, `vllm`, `lmstudio`, or a URL) |
| `--target NAME` | `-t` | string | none | Named LLM target from config |
| `--model NAME` | `-m` | string | none | LLM model name (e.g. `llama3`, `gpt-4o`) |
| `--system-prompt TEXT` | | string | none | System prompt for the LLM |
| `--set KEY=VALUE` | | string (repeatable) | none | LLM parameter (e.g. `temperature=0.7`) |
| `--api-key KEY` | | string | none | API key for the endpoint |

## Subcommands

### `dumpcat init`

Create a starter LLM profiles config at `~/.dumpcat/dumpcat_profiles.toml`:

```bash
dumpcat init
```

Use `--force` to overwrite an existing config:

```bash
dumpcat init --force
```

## Flag details

### `--output` / `-o` and `--output-append` / `-A`

Write output to a file. By default, `-o` overwrites the file. Use `-A` to append instead.

```bash
# Overwrite (default)
dumpcat -o dump.md

# Append to an existing file
dumpcat -o dump.md -A

# Accumulate multiple dumps
dumpcat src/ -i .py -o all-code.md -A
dumpcat tests/ -i .py -o all-code.md -A
```

### `--include` / `-i`

Filter by file extension. Repeatable. Only files matching at least one extension are included.

```bash
# Only Python and JavaScript files
dumpcat -i .py -i .js
```

!!! note
    Files with no extension are excluded when `--include` is active.

### `--exclude` / `-e`

Exclude files or directories matching glob patterns. Repeatable. Matches against file names, path components, and full relative paths.

```bash
# Exclude test files and cache directories
dumpcat -e tests -e "*.pyc" -e "__pycache__"
```

### `--prepend` / `--append`

Add text before or after the main output. Useful for adding LLM prompts.

- Plain string: used as-is
- `@filepath`: reads the file's contents

```bash
# Inline prompt
dumpcat -p "Review this code for security issues"

# From a file
dumpcat -p @prompts/review.md -a @prompts/footer.md
```

### `--max-size`

Skip files larger than the given size. Accepts human-readable sizes:

- `500b` — 500 bytes
- `50kb` — 50 kilobytes
- `1mb` — 1 megabyte (default)
- `1gb` — 1 gigabyte

```bash
dumpcat --max-size 500kb
```

### `--tree-only` / `--no-tree`

These flags are mutually exclusive.

```bash
# Just the tree structure
dumpcat --tree-only

# Just the file contents
dumpcat --no-tree
```

### `--config` / `--profile`

See [Configuration](configuration.md) for details on `.dumpcat.toml` and profiles.

```bash
# Use a specific config file and profile
dumpcat --config myconfig.toml --profile python
```

### `--llm`

Send the dump output to a local or remote LLM via an OpenAI-compatible chat completions API. The value can be a built-in provider name or a full URL:

- `ollama` — `http://localhost:11434/v1/chat/completions`
- `vllm` — `http://localhost:8000/v1/chat/completions`
- `lmstudio` — `http://localhost:1234/v1/chat/completions`
- Any `http://` or `https://` URL

```bash
# Use a built-in provider
dumpcat -i .py --llm ollama -m llama3

# Use a custom URL
dumpcat --llm http://localhost:9000/v1/chat/completions -m my-model
```

When `--llm` is used without a value, dumpcat looks for a `default_target` in the LLM config file (`~/.dumpcat/dumpcat_profiles.toml`). See [Configuration](configuration.md) for details.

The LLM response replaces the normal dump output on stdout. Use `-o` to write the response to a file instead.

### `--target` / `-t`

Use a named target from the LLM config file:

```bash
dumpcat --llm -t mylocal
```

### `--model` / `-m`

Specify the model name. Required unless the target config includes a model:

```bash
dumpcat --llm ollama -m llama3
```

### `--system-prompt`

Set a system prompt for the LLM request:

```bash
dumpcat --llm ollama -m llama3 --system-prompt "You are a code reviewer. Be concise."
```

### `--set`

Pass extra parameters to the LLM API. Repeatable. Values are auto-coerced to the correct type:

```bash
dumpcat --llm ollama -m llama3 --set temperature=0.5 --set max_tokens=4096
```

### `--api-key`

Provide an API key for authenticated endpoints:

```bash
dumpcat --llm https://api.openai.com/v1/chat/completions -m gpt-4o --api-key sk-...
```

For reusable setups, store the API key env var name in a target config instead. See [Configuration](configuration.md).
