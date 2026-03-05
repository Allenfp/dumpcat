import json

from dumpcat.formats import format_markdown, format_plain, format_json, _guess_language


def test_guess_language():
    assert _guess_language("test.py") == "python"
    assert _guess_language("src/main.js") == "javascript"
    assert _guess_language("Dockerfile") == "dockerfile"
    assert _guess_language("Makefile") == "makefile"
    assert _guess_language("noext") == ""


def test_format_markdown():
    files = [{"path": "test.py", "content": "print('hi')\n"}]
    result = format_markdown("test.py", files)
    assert "# File Tree" in result
    assert "# File Contents" in result
    assert "```python" in result
    assert "print('hi')" in result


def test_format_markdown_with_error():
    files = [{"path": "test.bin", "error": "[binary file skipped]"}]
    result = format_markdown(None, files)
    assert "[binary file skipped]" in result


def test_format_markdown_with_stats():
    files = [{"path": "test.py", "content": "x\n"}]
    stats = {"files": 1, "lines": 2, "est_tokens": 1}
    result = format_markdown(None, files, stats=stats)
    assert "# Stats" in result
    assert "Files: 1" in result


def test_format_markdown_prepend_append():
    result = format_markdown(None, [], prepend="BEFORE", append="AFTER")
    assert result.startswith("BEFORE")
    assert "AFTER" in result


def test_format_plain():
    files = [{"path": "test.py", "content": "print('hi')\n"}]
    result = format_plain("test.py", files)
    assert "=== TREE ===" in result
    assert "=== test.py ===" in result
    assert "print('hi')" in result


def test_format_json():
    entries = [{"path": "test.py", "is_dir": False}]
    files = [{"path": "test.py", "content": "print('hi')\n", "size": 12}]
    result = format_json(entries, files)
    data = json.loads(result)
    assert data["tree"] == ["test.py"]
    assert "print('hi')" in data["files"]["test.py"]["content"]


def test_format_markdown_line_numbers():
    files = [{"path": "test.py", "content": "a\nb\nc"}]
    result = format_markdown(None, files, line_numbers=True)
    assert "1 | a" in result
    assert "2 | b" in result
    assert "3 | c" in result
