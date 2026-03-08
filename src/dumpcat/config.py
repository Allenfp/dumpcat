from __future__ import annotations

import sys
import tomllib
from pathlib import Path


def find_config(start: Path, explicit: str | None = None) -> Path | None:
    if explicit:
        p = Path(explicit)
        return p if p.is_file() else None

    current = start.resolve()
    while True:
        candidate = current / ".dumpcat.toml"
        if candidate.is_file():
            return candidate
        parent = current.parent
        if parent == current:
            break
        current = parent

    xdg = Path.home() / ".config" / "dumpcat" / "config.toml"
    if xdg.is_file():
        return xdg

    return None


def load_config(
    config_path: Path | None, profile: str = "default"
) -> dict:
    if config_path is None:
        return {}

    try:
        with open(config_path, "rb") as f:
            data = tomllib.load(f)
    except (OSError, tomllib.TOMLDecodeError):
        return {}

    result = {}

    if "default" in data and isinstance(data["default"], dict):
        result.update(data["default"])

    if profile != "default":
        profiles = data.get("profiles", {})
        if profile in profiles and isinstance(profiles[profile], dict):
            result.update(profiles[profile])
        else:
            print(f"Warning: profile '{profile}' not found in config", file=sys.stderr)

    return result


def load_llm_config() -> dict:
    config_path = Path.home() / ".dumpcat" / "dumpcat_profiles.toml"
    if not config_path.is_file():
        return {}

    try:
        with open(config_path, "rb") as f:
            data = tomllib.load(f)
    except (OSError, tomllib.TOMLDecodeError):
        return {}

    return data.get("llm", {})


def merge_config(config: dict, cli_args: dict) -> dict:
    merged = dict(config)
    for key, value in cli_args.items():
        if value is not None:
            merged[key] = value
    return merged
