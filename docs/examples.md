# Examples

Real-world usage patterns for dumpcat.

## LLM code review

Dump your Python source with a review prompt:

```bash
dumpcat src/ -i .py -p "Review this code for bugs, security issues, and performance problems. Suggest concrete fixes."
```

## Project overview for onboarding

Generate a shallow tree with no file contents — great for showing project structure:

```bash
dumpcat -d 2 --tree-only
```

Output:

```
.
├── src/
│   └── dumpcat/
├── tests/
├── docs/
├── pyproject.toml
└── README.md
```

## Export codebase as JSON for tooling

Pipe structured output into another tool or script:

```bash
dumpcat -f json -s --no-tree -i .py | python process_codebase.py
```

## Dump with line numbers

Useful when you want to reference specific lines in your LLM prompt:

```bash
dumpcat src/ -i .py -n -p "There's a bug around line 42 in core.py. Can you find and fix it?"
```

## Compare two directories

Dump both and diff them:

```bash
dumpcat src/ -f plain -o src-dump.txt
dumpcat lib/ -f plain -o lib-dump.txt
diff src-dump.txt lib-dump.txt
```

## Exclude test files and generated code

```bash
dumpcat -e tests -e "*.generated.*" -e __pycache__ -e "*.pyc"
```

## Use with a prompt template file

Create a reusable prompt template:

```bash
echo "You are a senior Python developer. Review the following codebase for:
- Security vulnerabilities
- Performance issues
- Code style and best practices

Be specific and reference file paths and line numbers." > prompts/review.md
```

Then use it:

```bash
dumpcat src/ -i .py -p @prompts/review.md
```

## Full project dump with stats

```bash
dumpcat -s
```

```
# File Contents

...

# File Tree

```
.
├── src/
│   └── ...
└── README.md
```

# Stats

- Files: 15
- Lines: 1247
- Estimated tokens: 4800
```

## CI/CD: generate context for automated review

```bash
# In a GitHub Action or CI script
dumpcat src/ -i .py -f json -s -o context.json
# Feed context.json to an LLM API for automated review
```

## Only show the tree

```bash
dumpcat --tree-only
```

```
.
├── src/
│   └── dumpcat/
│       ├── __init__.py
│       ├── cli.py
│       ├── core.py
│       └── ...
├── tests/
│   └── ...
├── pyproject.toml
└── README.md
```

## Hidden files and symlinks

```bash
# Include dotfiles like .env, .eslintrc
dumpcat --hidden

# Follow symbolic links (with loop detection)
dumpcat --follow-symlinks
```
