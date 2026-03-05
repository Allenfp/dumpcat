from __future__ import annotations

import fnmatch
import os
from pathlib import Path

import pathspec


def parse_size(size_str: str) -> int:
    size_str = size_str.strip().lower()
    multipliers = {"b": 1, "kb": 1024, "mb": 1024**2, "gb": 1024**3}
    for suffix, mult in sorted(multipliers.items(), key=lambda x: -len(x[0])):
        if size_str.endswith(suffix):
            num = size_str[: -len(suffix)].strip()
            return int(float(num) * mult)
    return int(size_str)


def is_binary(file_path: Path) -> bool:
    with open(file_path, "rb") as f:
        chunk = f.read(8192)
        return b"\x00" in chunk


def load_gitignore_spec(root: Path) -> pathspec.PathSpec | None:
    gitignore_path = root / ".gitignore"
    if not gitignore_path.is_file():
        return None
    try:
        patterns = gitignore_path.read_text(encoding="utf-8").splitlines()
        return pathspec.PathSpec.from_lines("gitignore", patterns)
    except (OSError, PermissionError):
        return None


def should_include(
    path: Path,
    root: Path,
    *,
    include_exts: list[str] | None = None,
    exclude_patterns: list[str] | None = None,
    gitignore_spec: pathspec.PathSpec | None = None,
    max_size: int | None = None,
    hidden: bool = False,
    output_path: Path | None = None,
) -> bool:
    rel = path.relative_to(root)
    rel_str = str(rel)

    if output_path and path.resolve() == output_path.resolve():
        return False

    if not hidden:
        for part in rel.parts:
            if part.startswith(".") and part not in (".", ".."):
                return False

    if gitignore_spec and gitignore_spec.match_file(rel_str):
        return False

    if exclude_patterns:
        for pattern in exclude_patterns:
            if fnmatch.fnmatch(rel_str, pattern):
                return False
            if fnmatch.fnmatch(path.name, pattern):
                return False
            for part in rel.parts:
                if fnmatch.fnmatch(part, pattern):
                    return False

    if path.is_file():
        if include_exts:
            if not any(path.name.endswith(ext) for ext in include_exts):
                return False

        if max_size is not None:
            try:
                if path.stat().st_size > max_size:
                    return False
            except OSError:
                pass

    return True


def should_include_dir(
    path: Path,
    root: Path,
    *,
    exclude_patterns: list[str] | None = None,
    gitignore_spec: pathspec.PathSpec | None = None,
    hidden: bool = False,
) -> bool:
    rel = path.relative_to(root)
    rel_str = str(rel) + "/"

    if not hidden:
        for part in rel.parts:
            if part.startswith(".") and part not in (".", ".."):
                return False

    if gitignore_spec and gitignore_spec.match_file(rel_str):
        return False

    if exclude_patterns:
        for pattern in exclude_patterns:
            for part in rel.parts:
                if fnmatch.fnmatch(part, pattern):
                    return False

    return True
