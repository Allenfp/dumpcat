from __future__ import annotations

from pathlib import Path


def prune_empty_dirs(entries: list[dict]) -> list[dict]:
    """Remove directories that contain no files (recursively)."""
    file_paths = {e["path"] for e in entries if not e["is_dir"]}
    dirs_with_files: set[str] = set()
    for fp in file_paths:
        parts = fp.split("/")
        for i in range(1, len(parts)):
            dirs_with_files.add("/".join(parts[:i]))

    return [e for e in entries if not e["is_dir"] or e["path"] in dirs_with_files]


def _build_tree_nodes(entries: list[dict]) -> dict:
    """Build a nested dict representing the directory tree.

    Returns a dict mapping name -> {"is_dir": bool, "children": dict}.
    """
    root: dict = {}
    for entry in entries:
        parts = entry["path"].split("/")
        node = root
        for i, part in enumerate(parts[:-1]):
            if part not in node:
                node[part] = {"is_dir": True, "children": {}}
            node = node[part]["children"]
        name = parts[-1]
        if entry["is_dir"]:
            if name not in node:
                node[name] = {"is_dir": True, "children": {}}
        else:
            node[name] = {"is_dir": False, "children": {}}
    return root


def _render_nodes(nodes: dict, prefix: str, lines: list[str]) -> None:
    """Recursively render tree nodes with box-drawing characters."""
    items = sorted(nodes.items(), key=lambda x: (not x[1]["is_dir"], x[0].lower()))
    for i, (name, info) in enumerate(items):
        is_last = i == len(items) - 1
        connector = "└── " if is_last else "├── "
        display_name = f"{name}/" if info["is_dir"] else name
        lines.append(f"{prefix}{connector}{display_name}")
        if info["is_dir"] and info["children"]:
            extension = "    " if is_last else "│   "
            _render_nodes(info["children"], prefix + extension, lines)


def render_tree(
    entries: list[dict],
) -> str:
    """Render a tree structure from a list of entry dicts.

    Each entry has: path (relative str), is_dir (bool).
    Renders using box-drawing characters like the `tree` command.
    """
    pruned = prune_empty_dirs(entries)
    if not pruned:
        return "."
    tree_nodes = _build_tree_nodes(pruned)
    lines = ["."]
    _render_nodes(tree_nodes, "", lines)
    return "\n".join(lines)
