# dumpcat — Implementation Plan

## Context

**dumpcat** is a Python CLI tool that dumps a directory's file tree structure and text file contents into a single formatted output. Primary use case: preparing codebase context for LLM prompts. It will be published to PyPI.

The project currently has no Python code — just a README, LICENSE, .gitignore, and Docker dev environment.

## Decisions

- **CLI framework**: `argparse` (stdlib) — zero runtime deps for core functionality
- **Output formats**: Markdown (default), Plain, JSON
- **Config**: `.dumpcat.toml` with named profiles — good for adoption, lets users share project configs
- **Scope**: Full MVP in one pass
- **Package layout**: `src/dumpcat/` (PyPA-recommended for PyPI publishing)

## CLI Interface

```
dumpcat [OPTIONS] [PATH]
```

PATH defaults to `.` (current directory).

### Flags

| Flag | Short | Type | Default | Description |
|---|---|---|---|---|
| `--output` | `-o` | PATH | stdout | Output file path |
| `--clipboard` | `-c` | flag | false | Copy output to clipboard |
| `--depth` | `-d` | INT | unlimited | Max directory depth |
| `--include` | `-i` | STR+ | all | Include only these extensions (e.g. `-i .py -i .js`) |
| `--exclude` | `-e` | STR+ | none | Exclude glob patterns (e.g. `-e node_modules -e "*.pyc"`) |
| `--gitignore/--no-gitignore` | | flag | true | Respect .gitignore rules |
| `--tree-only` | | flag | false | Only show tree, no file contents |
| `--no-tree` | | flag | false | Only show file contents, no tree |
| `--prepend` | `-p` | STR | none | Text or `@filepath` to prepend |
| `--append` | `-a` | STR | none | Text or `@filepath` to append |
| `--max-size` | | STR | 1mb | Skip files larger than this |
| `--stats` | `-s` | flag | false | Show file count, lines, est. tokens |
| `--format` | `-f` | choice | markdown | `markdown`, `plain`, `json` |
| `--config` | | PATH | auto | Path to config file |
| `--profile` | | STR | default | Named profile from config |
| `--follow-symlinks` | | flag | false | Follow symbolic links |
| `--hidden` | | flag | false | Include dotfiles/dotdirs |
| `--line-numbers` | `-n` | flag | false | Add line numbers to content |

### Prepend/Append convention

- Plain string: used as-is (`-p "Review this code"`)
- `@filepath`: reads file contents (`-p @prompts/review.md`)

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

## Config File (`.dumpcat.toml`)

Auto-discovered by walking up from target dir, then `~/.config/dumpcat/config.toml`.

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

Precedence: defaults -> config `[default]` -> config `[profiles.X]` -> CLI flags.

## Project Structure

```
pyproject.toml
README.md
LICENSE
src/
  dumpcat/
    __init__.py        # Version
    cli.py             # Argparse setup, entry point
    core.py            # Orchestrator: walk, filter, read, format, output
    tree.py            # Tree rendering
    reader.py          # File reading, binary detection, encoding
    filters.py         # Include/exclude, gitignore, size limits
    config.py          # TOML config discovery, profile merging
    formats.py         # Markdown, Plain, JSON formatters
    clipboard.py       # Clipboard abstraction
    stats.py           # Token/line/file counting
tests/
  conftest.py          # Shared fixtures (temp directory trees)
  test_cli.py
  test_tree.py
  test_reader.py
  test_filters.py
  test_config.py
  test_formats.py
```

## Dependencies

### Runtime
| Package | Purpose | Notes |
|---|---|---|
| `pathspec` | .gitignore parsing | Small, no transitive deps. Required for gitignore support. |

That's it. `argparse` and `tomllib` (Python 3.11+) are stdlib. Clipboard uses platform commands (`pbcopy`/`xclip`/`clip.exe`) via subprocess — no `pyperclip` needed.

### Dev
`pytest`, `pytest-cov`, `ruff`, `build`

### Python version
3.11+ (for `tomllib` in stdlib).

## Edge Cases & Limitations

| Case | Handling |
|---|---|
| Binary files | Detect via null-byte check in first 8KB, skip with `[binary file skipped]` |
| Encoding | UTF-8 first, fallback to latin-1 |
| Permission errors | Catch per-file, log `[permission denied]`, continue |
| Symlink loops | Track visited inodes, skip revisits |
| Output file in scanned dir | Auto-exclude output path from scan |
| Very large dirs | Stream output (generator pattern), never buffer full output in memory (except clipboard) |
| Files with no extension | Included unless `--include` is active |
| Empty directories | Shown in tree, no content section |
| Large clipboard output | Warn if output exceeds 1MB going to clipboard |

## pyproject.toml Key Sections

```toml
[project]
name = "dumpcat"
version = "0.1.0"
description = "A CLI for dumping file system contents to terminal, files, or clipboard"
requires-python = ">=3.11"
license = "MIT"
dependencies = ["pathspec>=0.11"]

[project.scripts]
dumpcat = "dumpcat.cli:main"

[build-system]
requires = ["setuptools>=68.0"]
build-backend = "setuptools.backends._legacy:_Backend"
```

## Architecture Notes

- **Streaming**: Core orchestrator yields output line-by-line (generator). Low memory for file/stdout output. Clipboard must buffer.
- **Filter pipeline**: Composable list of `(path) -> bool` callables. Easy to extend.
- **Format strategy**: Each format is a class with `format_tree()`, `format_file_header()`, `format_file_content()`, etc. Orchestrator is format-agnostic.
- **Config merging**: defaults < config `[default]` < config `[profiles.X]` < CLI flags.

## Implementation Order

All in one pass (full MVP), files built in this logical order:

1. `pyproject.toml` — project metadata, deps, entry point
2. `src/dumpcat/__init__.py` — version
3. `src/dumpcat/filters.py` — include/exclude/gitignore/binary/size filtering
4. `src/dumpcat/reader.py` — file reading with encoding fallback
5. `src/dumpcat/tree.py` — tree rendering from directory walk
6. `src/dumpcat/formats.py` — markdown, plain, JSON formatters
7. `src/dumpcat/config.py` — TOML config discovery and profile merging
8. `src/dumpcat/stats.py` — counting utilities
9. `src/dumpcat/clipboard.py` — platform clipboard abstraction
10. `src/dumpcat/core.py` — orchestrator wiring everything together
11. `src/dumpcat/cli.py` — argparse CLI, calls core
12. `tests/` — test suite

## Verification

1. `pip install -e .` — install in dev mode
2. `dumpcat .` — dump current project to stdout (markdown)
3. `dumpcat -f plain -o dump.txt .` — dump to file in plain format
4. `dumpcat -d 2 -i .py .` — only Python files, 2 levels deep
5. `dumpcat -p "Analyze this code" -s .` — with prepend text and stats
6. `dumpcat --profile python .` — using a config profile
7. `pytest` — run test suite
