import pytest

from dumpcat.init import TEMPLATE, run_init


@pytest.fixture(autouse=True)
def patch_config_paths(monkeypatch, tmp_path):
    """Redirect config paths to tmp_path for all tests."""
    config_dir = tmp_path / ".dumpcat"
    config_file = config_dir / "dumpcat_profiles.toml"
    import dumpcat.init as init_mod

    monkeypatch.setattr(init_mod, "CONFIG_DIR", config_dir)
    monkeypatch.setattr(init_mod, "CONFIG_FILE", config_file)
    return config_dir, config_file


def test_init_creates_config(patch_config_paths, capsys):
    config_dir, config_file = patch_config_paths
    run_init([])
    assert config_file.exists()
    content = config_file.read_text()
    assert '[llm]' in content
    assert 'default_target = "ollama"' in content
    assert '[llm.targets.ollama]' in content
    assert '[llm.targets.vllm]' in content
    assert '[llm.targets.lmstudio]' in content
    captured = capsys.readouterr()
    assert "Created" in captured.err


def test_init_errors_if_exists(patch_config_paths, capsys):
    config_dir, config_file = patch_config_paths
    config_dir.mkdir(parents=True, exist_ok=True)
    config_file.write_text("existing")
    with pytest.raises(SystemExit) as exc_info:
        run_init([])
    assert exc_info.value.code == 1
    captured = capsys.readouterr()
    assert "already exists" in captured.err
    assert config_file.read_text() == "existing"


def test_init_force_overwrites(patch_config_paths, capsys):
    config_dir, config_file = patch_config_paths
    config_dir.mkdir(parents=True, exist_ok=True)
    config_file.write_text("existing")
    run_init(["--force"])
    assert TEMPLATE in config_file.read_text()


def test_init_via_cli(patch_config_paths, monkeypatch, capsys):
    """Test that `dumpcat init` dispatches correctly via CLI main."""
    config_dir, config_file = patch_config_paths
    from dumpcat.cli import main

    main(["init"])
    assert config_file.exists()
