from pathlib import Path

from dumpcat.config import find_config, load_config, merge_config


def test_find_config_in_dir(tmp_path):
    config = tmp_path / ".dumpcat.toml"
    config.write_text('[default]\nformat = "plain"\n')
    assert find_config(tmp_path) == config


def test_find_config_walks_up(tmp_path):
    config = tmp_path / ".dumpcat.toml"
    config.write_text('[default]\nformat = "plain"\n')
    subdir = tmp_path / "a" / "b"
    subdir.mkdir(parents=True)
    assert find_config(subdir) == config


def test_find_config_explicit(tmp_path):
    config = tmp_path / "custom.toml"
    config.write_text('[default]\nformat = "json"\n')
    assert find_config(tmp_path, str(config)) == config


def test_find_config_none(tmp_path):
    subdir = tmp_path / "empty"
    subdir.mkdir()
    # May find user's home config; just check it doesn't crash
    find_config(subdir)


def test_load_config(tmp_path):
    config = tmp_path / ".dumpcat.toml"
    config.write_text(
        '[default]\nformat = "plain"\nexclude = ["__pycache__"]\n\n'
        '[profiles.python]\ninclude = [".py"]\n'
    )
    result = load_config(config, "default")
    assert result["format"] == "plain"
    assert result["exclude"] == ["__pycache__"]


def test_load_config_profile(tmp_path):
    config = tmp_path / ".dumpcat.toml"
    config.write_text(
        '[default]\nformat = "plain"\n\n'
        '[profiles.python]\ninclude = [".py"]\nformat = "markdown"\n'
    )
    result = load_config(config, "python")
    assert result["format"] == "markdown"
    assert result["include"] == [".py"]


def test_load_config_none():
    assert load_config(None) == {}


def test_merge_config():
    config = {"format": "plain", "hidden": False}
    cli = {"format": "json", "depth": 3, "hidden": None}
    merged = merge_config(config, cli)
    assert merged["format"] == "json"
    assert merged["depth"] == 3
    assert merged["hidden"] is False
