# CLI Reference

```
dumpcat [OPTIONS] [PATH]
```

`PATH` defaults to `.` (current directory).

## Flags

| Flag | Short | Type | Default | Description |
|---|---|---|---|---|
| `--output PATH` | `-o` | string | stdout | Write output to a file |
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

## Flag details

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
