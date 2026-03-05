# dumpcat

A CLI tool that dumps a directory's file tree and contents into a single formatted output. Built for preparing codebase context for LLM prompts.

## Features

- Renders directory tree and file contents in **Markdown**, **Plain text**, or **JSON**
- Respects `.gitignore` by default
- Configurable include/exclude filters, depth limits, and file size limits
- Copy output directly to clipboard
- Prepend/append custom text or file contents (great for prompt templates)
- Project-level config via `.dumpcat.toml` with named profiles
- Line numbers, stats (file count, lines, estimated tokens), and more

## Installation

Requires **Python 3.11+**.

```bash
pip install dumpcat
```

Or install from source:

```bash
git clone https://github.com/your-username/dumpcat.git
cd dumpcat
pip install .
```

## Quick Start

```bash
# Dump current directory to stdout (Markdown format)
dumpcat

# Dump a specific directory
dumpcat src/

# Write output to a file
dumpcat -o dump.md

# Copy output to clipboard
dumpcat -c

# Only Python files, 2 levels deep
dumpcat -d 2 -i .py

# Plain text format with stats
dumpcat -f plain -s

# Prepend a prompt for an LLM
dumpcat -p "Review this code for bugs"

# Prepend from a file
dumpcat -p @prompts/review.md

# Show only the tree structure
dumpcat --tree-only

# JSON output, no tree
dumpcat --no-tree -f json
```

## CLI Reference

```
dumpcat [OPTIONS] [PATH]
```

`PATH` defaults to `.` (current directory).

### Examples

**Dump only Python files to clipboard with a review prompt:**

```bash
dumpcat -i .py -c -p "Review this code for security issues"
```

**Export a shallow overview of a project in plain text:**

```bash
dumpcat -d 2 --tree-only -f plain -o overview.txt src/
```

**Generate JSON output with stats and line numbers, excluding tests:**

```bash
dumpcat -f json -s -n -e tests -e "*.pyc" -o codebase.json
```

### Flags

| Flag | Short | Description |
|------|-------|-------------|
| `--output PATH` | `-o` | Write output to a file instead of stdout |
| `--clipboard` | `-c` | Copy output to clipboard |
| `--depth INT` | `-d` | Max directory depth |
| `--include EXT` | `-i` | Include only these extensions (repeatable: `-i .py -i .js`) |
| `--exclude PATTERN` | `-e` | Exclude glob patterns (repeatable: `-e node_modules -e "*.pyc"`) |
| `--gitignore / --no-gitignore` | | Respect `.gitignore` rules (default: on) |
| `--tree-only` | | Only show tree, no file contents |
| `--no-tree` | | Only show file contents, no tree |
| `--prepend TEXT` | `-p` | Text or `@filepath` to prepend to output |
| `--append TEXT` | `-a` | Text or `@filepath` to append to output |
| `--max-size SIZE` | | Skip files larger than this (default: `1mb`) |
| `--stats` | `-s` | Show file count, lines, and estimated tokens |
| `--format FORMAT` | `-f` | Output format: `markdown`, `plain`, or `json` (default: `markdown`) |
| `--config PATH` | | Path to config file |
| `--profile NAME` | | Named profile from config (default: `default`) |
| `--follow-symlinks` | | Follow symbolic links |
| `--hidden` | | Include dotfiles and dotdirs |
| `--line-numbers` | `-n` | Add line numbers to file contents |
| `--version` | `-V` | Show version |

## Output Formats

### Markdown (default)

````
# File Tree

```
src/
  main.py
  utils/
    helpers.py
```

# File Contents

## `src/main.py`

```python
import sys
...
```
````

### Plain

```
=== TREE ===

src/
  main.py
  utils/
    helpers.py

=== src/main.py ===

import sys
...
```

### JSON

```json
{
  "tree": ["src/main.py", "src/utils/helpers.py"],
  "files": {
    "src/main.py": {
      "content": "import sys\n...",
      "lines": 42,
      "size": 1024
    }
  },
  "stats": { "files": 2, "lines": 84, "est_tokens": 1200 }
}
```

## Configuration

Create a `.dumpcat.toml` in your project root (or `~/.config/dumpcat/config.toml` for global defaults). The config file is auto-discovered by walking up from the target directory.

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

Use profiles with:

```bash
dumpcat --profile python
```

**Precedence:** defaults < config `[default]` < config `[profiles.X]` < CLI flags.

## Development

```bash
git clone https://github.com/your-username/dumpcat.git
cd dumpcat
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
pytest
```

## License

[MIT](LICENSE)
