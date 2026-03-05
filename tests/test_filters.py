from pathlib import Path

from dumpcat.filters import is_binary, parse_size, should_include, load_gitignore_spec, should_include_dir


def test_parse_size():
    assert parse_size("1mb") == 1024 * 1024
    assert parse_size("500kb") == 500 * 1024
    assert parse_size("1gb") == 1024**3
    assert parse_size("100b") == 100
    assert parse_size("2048") == 2048


def test_is_binary(tmp_path):
    text_file = tmp_path / "test.txt"
    text_file.write_text("hello world")
    assert not is_binary(text_file)

    bin_file = tmp_path / "test.bin"
    bin_file.write_bytes(b"\x00\x01\x02\x03")
    assert is_binary(bin_file)


def test_should_include_basic(tmp_path):
    f = tmp_path / "test.py"
    f.write_text("print('hi')")

    assert should_include(f, tmp_path)
    assert should_include(f, tmp_path, include_exts=[".py"])
    assert not should_include(f, tmp_path, include_exts=[".js"])


def test_should_include_exclude_pattern(tmp_path):
    f = tmp_path / "test.pyc"
    f.write_bytes(b"\x00")

    assert not should_include(f, tmp_path, exclude_patterns=["*.pyc"])


def test_should_include_hidden(tmp_path):
    hidden_dir = tmp_path / ".hidden"
    hidden_dir.mkdir()
    f = hidden_dir / "secret.txt"
    f.write_text("secret")

    assert not should_include(f, tmp_path, hidden=False)
    assert should_include(f, tmp_path, hidden=True)


def test_should_include_max_size(tmp_path):
    f = tmp_path / "big.txt"
    f.write_text("x" * 1000)

    assert should_include(f, tmp_path, max_size=2000)
    assert not should_include(f, tmp_path, max_size=500)


def test_gitignore_spec(tmp_project_with_gitignore):
    root = tmp_project_with_gitignore
    spec = load_gitignore_spec(root)
    assert spec is not None

    cache_file = root / "__pycache__" / "main.cpython-311.pyc"
    assert not should_include(cache_file, root, gitignore_spec=spec)


def test_should_include_dir_hidden(tmp_path):
    d = tmp_path / ".hidden"
    d.mkdir()
    assert not should_include_dir(d, tmp_path, hidden=False)
    assert should_include_dir(d, tmp_path, hidden=True)


def test_should_include_dir_exclude(tmp_path):
    d = tmp_path / "node_modules"
    d.mkdir()
    assert not should_include_dir(d, tmp_path, exclude_patterns=["node_modules"])


def test_output_path_excluded(tmp_path):
    f = tmp_path / "output.md"
    f.write_text("output")
    assert not should_include(f, tmp_path, output_path=f)
