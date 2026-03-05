from __future__ import annotations


def compute_stats(files: list[dict], file_count: int | None = None) -> dict:
    total_lines = 0
    total_files = 0
    total_chars = 0

    for f in files:
        content = f.get("content")
        if content is not None:
            total_files += 1
            total_lines += content.count("\n") + 1 if content else 0
            total_chars += len(content)

    if file_count is not None:
        total_files = file_count

    est_tokens = total_chars // 4

    return {
        "files": total_files,
        "lines": total_lines,
        "est_tokens": est_tokens,
    }
