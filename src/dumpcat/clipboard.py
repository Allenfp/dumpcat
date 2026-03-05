from __future__ import annotations

import platform
import subprocess
import sys


def copy_to_clipboard(text: str) -> bool:
    system = platform.system()
    try:
        if system == "Darwin":
            proc = subprocess.Popen(["pbcopy"], stdin=subprocess.PIPE)
            proc.communicate(text.encode("utf-8"))
            return proc.returncode == 0
        elif system == "Linux":
            for cmd in (["xclip", "-selection", "clipboard"], ["xsel", "--clipboard", "--input"]):
                try:
                    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
                    proc.communicate(text.encode("utf-8"))
                    if proc.returncode == 0:
                        return True
                except FileNotFoundError:
                    continue
            return False
        elif system == "Windows":
            proc = subprocess.Popen(["clip.exe"], stdin=subprocess.PIPE)
            proc.communicate(text.encode("utf-16le"))
            return proc.returncode == 0
        else:
            return False
    except Exception:
        return False


def warn_large_clipboard(size: int, threshold: int = 1024 * 1024) -> None:
    if size > threshold:
        print(
            f"Warning: clipboard output is {size / 1024 / 1024:.1f}MB",
            file=sys.stderr,
        )
