# Getting Started

## Installation

=== "pip"

    ```bash
    pip install dumpcat
    ```

=== "pipx (isolated)"

    ```bash
    pipx install dumpcat
    ```

=== "From source"

    ```bash
    git clone https://github.com/Allenfp/dumpcat.git
    cd dumpcat
    pip install .
    ```

## Basic usage

Run `dumpcat` in any directory to dump its file tree and contents as Markdown:

```bash
dumpcat
```

Dump a specific directory:

```bash
dumpcat src/
```

## Filtering files

Only include certain extensions:

```bash
dumpcat -i .py -i .js
```

Exclude patterns:

```bash
dumpcat -e node_modules -e "*.pyc"
```

Limit directory depth:

```bash
dumpcat -d 2
```

## Output options

Write to a file instead of stdout:

```bash
dumpcat -o dump.md
```

Copy to clipboard:

```bash
dumpcat -c
```

Switch output format:

```bash
# Plain text
dumpcat -f plain

# JSON
dumpcat -f json
```

## Prepending prompts

Add context for your LLM at the top of the output:

```bash
dumpcat -p "Review this code for bugs and suggest improvements"
```

Or read from a prompt template file:

```bash
dumpcat -p @prompts/review.md
```

## Show stats

Get a summary of file count, lines, and estimated tokens:

```bash
dumpcat -s
```

## What's next?

- See the full [CLI Reference](cli-reference.md) for every flag
- Learn about [Output Formats](output-formats.md)
- Set up project-level [Configuration](configuration.md) with `.dumpcat.toml`
- Browse real-world [Examples](examples.md)
