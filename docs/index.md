# dumpcat

**Dump a directory's file tree and contents into a single formatted output — built for LLM prompts.**

---

dumpcat scans a directory, builds a file tree, reads text file contents, and outputs everything in a clean format you can paste straight into ChatGPT, Claude, or any LLM.

## Why dumpcat?

When working with LLMs, you often need to share your codebase as context. Manually copying files is tedious and error-prone. dumpcat automates this:

- **One command** to dump your entire project (or a filtered slice of it)
- **Smart defaults** — respects `.gitignore`, skips binaries, limits file sizes
- **Multiple formats** — Markdown, plain text, or JSON
- **Configurable** — filter by extension, depth, glob patterns, or named profiles

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
