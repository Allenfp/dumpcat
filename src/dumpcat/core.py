from __future__ import annotations

import sys
from pathlib import Path

from .config import find_config, load_config, merge_config
from .filters import (
    load_gitignore_spec,
    parse_size,
    should_include,
    should_include_dir,
)
from .formats import format_json, format_markdown, format_plain
from .reader import read_file
from .stats import compute_stats
from .tree import render_tree


def resolve_text_arg(value: str | None) -> str | None:
    if value is None:
        return None
    if value.startswith("@"):
        filepath = Path(value[1:])
        try:
            return filepath.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            print(f"Warning: could not read {filepath}", file=sys.stderr)
            return None
    return value


def walk_directory(
    root: Path,
    *,
    depth: int | None = None,
    include_exts: list[str] | None = None,
    exclude_patterns: list[str] | None = None,
    gitignore_spec=None,
    max_size: int | None = None,
    hidden: bool = False,
    follow_symlinks: bool = False,
    output_path: Path | None = None,
) -> list[dict]:
    entries = []
    visited_inodes: set[tuple[int, int]] = set()

    def _walk(current: Path, current_depth: int):
        if depth is not None and current_depth > depth:
            return

        try:
            children = sorted(current.iterdir(), key=lambda p: (not p.is_dir(), p.name.lower()))
        except PermissionError:
            return

        for child in children:
            if child.name == ".git":
                continue

            is_symlink = child.is_symlink()

            if is_symlink and not follow_symlinks:
                continue

            if is_symlink and child.is_dir():
                try:
                    real = child.resolve()
                    st = real.stat()
                    inode_key = (st.st_dev, st.st_ino)
                    if inode_key in visited_inodes:
                        continue
                    visited_inodes.add(inode_key)
                except OSError:
                    continue

            if child.is_dir():
                if not should_include_dir(
                    child,
                    root,
                    exclude_patterns=exclude_patterns,
                    gitignore_spec=gitignore_spec,
                    hidden=hidden,
                ):
                    continue
                rel = str(child.relative_to(root))
                entries.append({"path": rel, "is_dir": True})
                _walk(child, current_depth + 1)
            elif child.is_file():
                if not should_include(
                    child,
                    root,
                    include_exts=include_exts,
                    exclude_patterns=exclude_patterns,
                    gitignore_spec=gitignore_spec,
                    max_size=max_size,
                    hidden=hidden,
                    output_path=output_path,
                ):
                    continue
                rel = str(child.relative_to(root))
                entries.append({"path": rel, "is_dir": False})

    _walk(root, 0)
    return entries


def run(args) -> None:
    root = Path(args.path).resolve()
    if not root.is_dir():
        print(f"Error: {args.path} is not a directory", file=sys.stderr)
        sys.exit(1)

    output_path = Path(args.output).resolve() if args.output else None

    config_path = find_config(root, args.config)
    config = load_config(config_path, args.profile)

    cli_overrides = {}
    if args.include:
        cli_overrides["include"] = args.include
    if args.exclude:
        cli_overrides["exclude"] = args.exclude
    if args.depth is not None:
        cli_overrides["depth"] = args.depth
    if args.format != "markdown":
        cli_overrides["format"] = args.format
    if args.hidden:
        cli_overrides["hidden"] = args.hidden
    if args.max_size != "1mb":
        cli_overrides["max_size"] = args.max_size

    merged = merge_config(config, cli_overrides)

    include_exts = merged.get("include")
    exclude_patterns = merged.get("exclude")
    max_depth = merged.get("depth")
    fmt = merged.get("format", "markdown")
    hidden = merged.get("hidden", False)
    max_size_str = merged.get("max_size", "1mb")
    max_size = parse_size(str(max_size_str))
    use_gitignore = args.gitignore

    gitignore_spec = load_gitignore_spec(root) if use_gitignore else None

    entries = walk_directory(
        root,
        depth=max_depth,
        include_exts=include_exts,
        exclude_patterns=exclude_patterns,
        gitignore_spec=gitignore_spec,
        max_size=max_size,
        hidden=hidden,
        follow_symlinks=args.follow_symlinks,
        output_path=output_path,
    )

    file_entries = [e for e in entries if not e["is_dir"]]
    files_data = []
    if not args.tree_only:
        for entry in file_entries:
            file_path = root / entry["path"]
            content, error = read_file(file_path)
            file_info = {"path": entry["path"]}
            if error:
                file_info["error"] = error
            else:
                file_info["content"] = content
                try:
                    file_info["size"] = file_path.stat().st_size
                except OSError:
                    file_info["size"] = 0
            files_data.append(file_info)

    show_tree = not args.no_tree
    prepend = resolve_text_arg(args.prepend)
    append = resolve_text_arg(args.append)

    if args.stats:
        file_count = len(file_entries) if args.tree_only else None
        stats = compute_stats(files_data, file_count=file_count)
    else:
        stats = None

    if fmt == "json":
        tree_for_json = entries if show_tree else None
        output = format_json(
            tree_for_json,
            files_data,
            prepend=prepend,
            append=append,
            stats=stats,
            line_numbers=args.line_numbers,
        )
    else:
        tree_str = render_tree(entries) if show_tree else None
        formatter = format_markdown if fmt == "markdown" else format_plain
        output = formatter(
            tree_str,
            files_data,
            prepend=prepend,
            append=append,
            stats=stats,
            line_numbers=args.line_numbers,
        )

    if args.output:
        Path(args.output).write_text(output, encoding="utf-8")
        print(f"Output written to {args.output}", file=sys.stderr)
    else:
        print(output)
