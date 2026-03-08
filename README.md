# Dumpcat

[![PyPI](https://img.shields.io/pypi/v/dumpcat.svg)](https://pypi.python.org/pypi/dumpcat)
[![License](https://img.shields.io/pypi/l/dumpcat.svg)](https://pypi.python.org/pypi/dumpcat)

A lightweight CLI for dumping directory contents and automating LLM workflows from the command line.

<p align="center">
  <img src="assets/dumpcat.png" alt="Dumpcat" width="300">
</p>

## Highlights

Use it for simple things like printing files to your terminal, or for advanced cases like automating LLM-powered processes in bash scripts and cron jobs.

- **One command** to dump your entire codebase (or a filtered slice of it) into a single output
- **Built-in LLM support** — send output to any OpenAI-compatible API (Ollama, vLLM, LM Studio, OpenAI, etc.)
- **Automation-ready** — prepend/append prompt templates, append to files, schedule with cron
- **Smart defaults** — respects `.gitignore`, skips binaries, limits file sizes
- **Filterable** — by extension, glob pattern, depth, and file size
- **Three output formats** — Markdown, plain text, or JSON
- **Configurable** — project-level `.dumpcat.toml` with named profiles and LLM targets
- **Zero bloat** — one runtime dependency (`pathspec`), everything else is stdlib

## Installation

Requires **Python 3.11+**.

```bash
uv tool install dumpcat
```

```bash
# Or with pip
pip install dumpcat
```

```bash
# Or from source
git clone https://github.com/Allenfp/dumpcat.git
cd dumpcat
pip install .
```

## Quick start

```bash
# Dump current directory as Markdown
dumpcat

# Only Python files, 2 levels deep
dumpcat -d 2 -i .py

# Prepend a prompt
dumpcat -i .py -p "Review this code for security issues"

# Plain text with stats
dumpcat -f plain -s

# Just the tree structure
dumpcat --tree-only

# JSON output for tooling
dumpcat -f json --no-tree

# Send to a local LLM
dumpcat -i .py --llm ollama -m llama3 -p "Review this code"

# Set up LLM profiles
dumpcat init
```

## Output

Dumpcat renders file contents followed by a file tree:

````
# File Contents

## `src/main.py`

```python
import sys

def main():
    print("hello")
```

# File Tree

```
.
├── src/
│   ├── main.py
│   └── utils/
│       └── helpers.py
└── README.md
```
````

See the [output formats documentation](https://allenfp.github.io/dumpcat/output-formats/) for Markdown, plain text, and JSON examples.

## CLI reference

```
dumpcat [OPTIONS] [PATH]
```

| Flag | Short | Description |
|---|---|---|
| `--output PATH` | `-o` | Write output to a file |
| `--output-append` | `-A` | Append to output file instead of overwriting |
| `--depth INT` | `-d` | Max directory depth |
| `--include EXT` | `-i` | Include only these extensions (repeatable) |
| `--exclude PATTERN` | `-e` | Exclude glob patterns (repeatable) |
| `--gitignore / --no-gitignore` | | Respect `.gitignore` rules (default: on) |
| `--tree-only` | | Show only the tree, no file contents |
| `--no-tree` | | Show only file contents, no tree |
| `--prepend TEXT` | `-p` | Text or `@filepath` to prepend |
| `--append TEXT` | `-a` | Text or `@filepath` to append |
| `--max-size SIZE` | | Skip files larger than this (default: `1mb`) |
| `--stats` | `-s` | Show file count, lines, and estimated tokens |
| `--format FORMAT` | `-f` | `markdown`, `plain`, or `json` (default: `markdown`) |
| `--config PATH` | | Path to config file |
| `--profile NAME` | | Named profile from config |
| `--follow-symlinks` | | Follow symbolic links |
| `--hidden` | | Include dotfiles and dotdirs |
| `--line-numbers` | `-n` | Add line numbers to file contents |
| `--llm PROVIDER` | | Send output to an LLM (`ollama`, `vllm`, `lmstudio`, or a URL) |
| `--target NAME` | `-t` | Named LLM target from config |
| `--model NAME` | `-m` | LLM model name |
| `--system-prompt TEXT` | | System prompt for the LLM |
| `--set KEY=VALUE` | | LLM parameter (repeatable) |
| `--api-key KEY` | | API key for the endpoint |

See the [full CLI reference](https://allenfp.github.io/dumpcat/cli-reference/) for details.

## Configuration

Create a `.dumpcat.toml` in your project root:

```toml
[default]
exclude = ["__pycache__", "*.pyc", ".venv"]

[profiles.python]
include = [".py", ".pyi", ".toml", ".md"]
exclude = ["__pycache__", "*.pyc", ".venv", ".mypy_cache"]

[profiles.web]
include = [".js", ".ts", ".tsx", ".css", ".html"]
exclude = ["node_modules", "dist", ".next"]
```

```bash
dumpcat --profile python
```

See the [configuration documentation](https://allenfp.github.io/dumpcat/configuration/) for details.

## Example workflows

### 1. Dump Python files to terminal

```bash
dumpcat src/ -d 2 -i .py
```

```
 ┌───────────┐       ┌─────────────┐       ┌───────────┐
 │  src/     │       │             │       │  stdout   │
 │  *.py     │ ────► │   dumpcat   │ ────► │           │
 │  depth 2  │       │             │       │  tree +   │
 └───────────┘       └─────────────┘       │  code     │
                                           └───────────┘
```

### 2. Send to a local LLM for review

```bash
dumpcat src/ -d 2 -i .py --llm ollama -m qwen3-vl-8b -p "Review this code for bugs"
```

```
 ┌───────────┐       ┌─────────────┐       ┌───────────┐       ┌───────────┐
 │  src/     │       │             │       │  Ollama   │       │  stdout   │
 │  *.py     │ ────► │   dumpcat   │ ────► │  qwen3   │ ────► │           │
 │  depth 2  │       │             │       │  -vl-8b  │       │  review   │
 └───────────┘       └─────────────┘       └───────────┘       └───────────┘
```

### 3. Scheduled LLM review appended to a CSV log

```bash
0 9 * * * dumpcat /path/to/project -d 2 -i .py -e "*.txt" -e "*.md" \
  -p @prompts/csv-review.md -a @prompts/csv-footer.md \
  --llm ollama -m qwen3-vl-8b --set temperature=0.5 \
  -o /path/to/reviews.csv -A
```

```
 ┌───────────┐   ┌──────────────┐   ┌─────────────┐   ┌───────────┐   ┌──────────────┐
 │  cron     │   │ prompts/     │   │             │   │  Ollama   │   │ reviews.csv  │
 │  daily    │──►│ -p csv-      │──►│   dumpcat   │──►│  qwen3   │──►│              │
 │  9:00 AM  │   │    review.md │   │  -i .py     │   │  -vl-8b  │   │ (append -A)  │
 └───────────┘   │ -a csv-      │   │  -e *.txt   │   │  temp=0.5│   └──────────────┘
                 │    footer.md │   │  -e *.md    │   └───────────┘
                 └──────────────┘   └─────────────┘        │
                                                           │
                                              each run appends a line:
                                              2025-03-01,main.py,high,SQL injection ...
                                              2025-03-02,helpers.py,low,unused import ...
                                              2025-03-03,main.py,med,missing null check ...
```

## Documentation

Full documentation is available at [allenfp.github.io/dumpcat](https://allenfp.github.io/dumpcat/).

## License

[MIT](LICENSE)
