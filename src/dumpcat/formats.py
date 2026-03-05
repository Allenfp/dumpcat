from __future__ import annotations

import json


EXTENSION_LANGUAGES = {
    ".py": "python",
    ".pyi": "python",
    ".js": "javascript",
    ".jsx": "javascript",
    ".ts": "typescript",
    ".tsx": "typescript",
    ".rs": "rust",
    ".go": "go",
    ".rb": "ruby",
    ".java": "java",
    ".kt": "kotlin",
    ".c": "c",
    ".h": "c",
    ".cpp": "cpp",
    ".hpp": "cpp",
    ".cs": "csharp",
    ".swift": "swift",
    ".sh": "bash",
    ".bash": "bash",
    ".zsh": "zsh",
    ".fish": "fish",
    ".html": "html",
    ".htm": "html",
    ".css": "css",
    ".scss": "scss",
    ".sass": "sass",
    ".less": "less",
    ".json": "json",
    ".yaml": "yaml",
    ".yml": "yaml",
    ".toml": "toml",
    ".ini": "ini",
    ".cfg": "ini",
    ".xml": "xml",
    ".sql": "sql",
    ".md": "markdown",
    ".rst": "rst",
    ".tex": "latex",
    ".lua": "lua",
    ".r": "r",
    ".R": "r",
    ".php": "php",
    ".pl": "perl",
    ".ex": "elixir",
    ".exs": "elixir",
    ".erl": "erlang",
    ".hs": "haskell",
    ".ml": "ocaml",
    ".vim": "vim",
    ".dockerfile": "dockerfile",
    ".tf": "hcl",
    ".proto": "protobuf",
    ".graphql": "graphql",
    ".vue": "vue",
    ".svelte": "svelte",
}


def _guess_language(path: str) -> str:
    name = path.rsplit("/", 1)[-1] if "/" in path else path
    lower = name.lower()
    if lower == "dockerfile":
        return "dockerfile"
    if lower == "makefile":
        return "makefile"
    if lower in ("cmakelists.txt",):
        return "cmake"
    dot = name.rfind(".")
    if dot == -1:
        return ""
    ext = name[dot:]
    return EXTENSION_LANGUAGES.get(ext, "")


def _add_line_numbers(content: str) -> str:
    lines = content.split("\n")
    width = len(str(len(lines)))
    return "\n".join(f"{i + 1:>{width}} | {line}" for i, line in enumerate(lines))


def format_markdown(
    tree_str: str | None,
    files: list[dict],
    *,
    prepend: str | None = None,
    append: str | None = None,
    stats: dict | None = None,
    line_numbers: bool = False,
) -> str:
    parts = []

    if prepend:
        parts.append(prepend)
        parts.append("")

    if files:
        parts.append("# File Contents")
        parts.append("")
        for f in files:
            parts.append(f"## `{f['path']}`")
            parts.append("")
            lang = _guess_language(f["path"])
            content = f.get("content")
            error = f.get("error")
            if error:
                parts.append(f"_{error}_")
            elif content is not None:
                if line_numbers:
                    content = _add_line_numbers(content)
                parts.append(f"```{lang}")
                parts.append(content)
                parts.append("```")
            parts.append("")

    if tree_str is not None:
        parts.append("# File Tree")
        parts.append("")
        parts.append("```")
        parts.append(tree_str)
        parts.append("```")
        parts.append("")

    if stats:
        parts.append("# Stats")
        parts.append("")
        parts.append(f"- Files: {stats['files']}")
        parts.append(f"- Lines: {stats['lines']}")
        parts.append(f"- Estimated tokens: {stats['est_tokens']}")
        parts.append("")

    if append:
        parts.append(append)
        parts.append("")

    return "\n".join(parts)


def format_plain(
    tree_str: str | None,
    files: list[dict],
    *,
    prepend: str | None = None,
    append: str | None = None,
    stats: dict | None = None,
    line_numbers: bool = False,
) -> str:
    parts = []

    if prepend:
        parts.append(prepend)
        parts.append("")

    for f in files:
        parts.append(f"=== {f['path']} ===")
        parts.append("")
        content = f.get("content")
        error = f.get("error")
        if error:
            parts.append(error)
        elif content is not None:
            if line_numbers:
                content = _add_line_numbers(content)
            parts.append(content)
        parts.append("")

    if tree_str is not None:
        parts.append("=== TREE ===")
        parts.append("")
        parts.append(tree_str)
        parts.append("")

    if stats:
        parts.append("=== STATS ===")
        parts.append("")
        parts.append(f"Files: {stats['files']}")
        parts.append(f"Lines: {stats['lines']}")
        parts.append(f"Estimated tokens: {stats['est_tokens']}")
        parts.append("")

    if append:
        parts.append(append)
        parts.append("")

    return "\n".join(parts)


def format_json(
    tree_entries: list[dict] | None,
    files: list[dict],
    *,
    prepend: str | None = None,
    append: str | None = None,
    stats: dict | None = None,
    line_numbers: bool = False,
) -> str:
    result = {}

    if prepend:
        result["prepend"] = prepend

    files_dict = {}
    for f in files:
        entry = {}
        content = f.get("content")
        error = f.get("error")
        if error:
            entry["error"] = error
        elif content is not None:
            if line_numbers:
                content = _add_line_numbers(content)
            entry["content"] = content
            entry["lines"] = content.count("\n") + 1 if content else 0
            entry["size"] = f.get("size", 0)
        files_dict[f["path"]] = entry
    result["files"] = files_dict

    if tree_entries is not None:
        result["tree"] = [e["path"] for e in tree_entries if not e["is_dir"]]

    if stats:
        result["stats"] = stats

    if append:
        result["append"] = append

    return json.dumps(result, indent=2)
