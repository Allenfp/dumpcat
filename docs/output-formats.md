# Output Formats

Dumpcat supports three output formats: **Markdown** (default), **Plain text**, and **JSON**.

## Markdown

The default format. Great for pasting into LLM chat interfaces that render Markdown.

```bash
dumpcat -f markdown
```

````markdown
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
│   └── main.py
└── README.md
```
````

File contents are wrapped in fenced code blocks with language detection based on file extension.

### Supported languages

Dumpcat auto-detects syntax highlighting for: Python, JavaScript, TypeScript, Rust, Go, Ruby, Java, Kotlin, C/C++, C#, Swift, Bash, HTML, CSS, SCSS, JSON, YAML, TOML, SQL, Markdown, Lua, R, PHP, Perl, Elixir, Erlang, Haskell, OCaml, HCL, Protobuf, GraphQL, Vue, Svelte, and more.

## Plain text

A clean, no-frills format.

```bash
dumpcat -f plain
```

```text
=== src/main.py ===

import sys

def main():
    print("hello")

=== TREE ===

.
├── src/
│   └── main.py
└── README.md
```

## JSON

Structured output for programmatic consumption.

```bash
dumpcat -f json
```

```json
{
  "files": {
    "src/main.py": {
      "content": "import sys\n\ndef main():\n    print(\"hello\")\n",
      "lines": 4,
      "size": 42
    }
  },
  "tree": [
    "src/main.py",
    "README.md"
  ]
}
```

The JSON format includes:

- `files` — object mapping file paths to their content, line count, and size
- `tree` — flat list of file paths (directories are excluded)
- `prepend` / `append` — included if `--prepend` / `--append` is used
- `stats` — included if `--stats` is used

## Line numbers

Add line numbers to file contents in any format:

```bash
dumpcat -n
```

```python
1 | import sys
2 |
3 | def main():
4 |     print("hello")
```

## Stats

Append a summary section with `--stats` / `-s`:

```bash
dumpcat -s
```

```
# Stats

- Files: 12
- Lines: 847
- Estimated tokens: 3200
```

Token estimation uses a simple `characters / 4` heuristic.
