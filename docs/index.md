# Dumpcat

**A lightweight CLI for dumping directory contents and automating LLM workflows from the command line.**

---

Use it for simple things like printing files to your terminal, or for advanced cases like automating LLM-powered processes in bash scripts and cron jobs. Dumpcat scans a directory, builds a file tree, reads text file contents, and outputs everything in a clean format — or sends it straight to any OpenAI-compatible API.

## Why Dumpcat?

- **One command** to dump your entire project (or a filtered slice of it)
- **Built-in LLM support** — send output to any OpenAI-compatible API (Ollama, vLLM, LM Studio, OpenAI, etc.)
- **Automation-ready** — prepend/append prompt templates, append to files, schedule with cron
- **Smart defaults** — respects `.gitignore`, skips binaries, limits file sizes
- **Multiple formats** — Markdown, plain text, or JSON
- **Configurable** — filter by extension, depth, glob patterns, named profiles, and LLM targets

## Quick example

```bash
# Dump current directory as Markdown
dumpcat

# Only Python files, 2 levels deep, with stats
dumpcat -d 2 -i .py -s

# Prepend a prompt
dumpcat -i .py -p "Review this code for security issues"
```

Output:

````
# File Contents

## `src/main.py`

```python
import sys
...
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

## Installation

Requires **Python 3.11+**.

```bash
uv tool install dumpcat
```

Or with pip:

```bash
pip install dumpcat
```

---

Ready to get started? Head to the [Getting Started](getting-started.md) guide.
