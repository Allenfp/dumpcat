from __future__ import annotations

from pathlib import Path

from .filters import is_binary


def read_file(path: Path) -> tuple[str | None, str | None]:
    """Read a file and return (content, error).

    Returns (content, None) on success, (None, error_message) on failure.
    """
    try:
        if is_binary(path):
            return None, "[binary file skipped]"
    except PermissionError:
        return None, "[permission denied]"
    except OSError as e:
        return None, f"[error reading file: {e}]"

    try:
        return path.read_text(encoding="utf-8"), None
    except UnicodeDecodeError:
        pass
    except PermissionError:
        return None, "[permission denied]"
    except OSError as e:
        return None, f"[error reading file: {e}]"

    try:
        return path.read_text(encoding="latin-1"), None
    except PermissionError:
        return None, "[permission denied]"
    except OSError as e:
        return None, f"[error reading file: {e}]"
