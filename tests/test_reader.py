from pathlib import Path

from dumpcat.reader import read_file


def test_read_text_file(tmp_path):
    f = tmp_path / "test.py"
    f.write_text("print('hello')\n")
    content, error = read_file(f)
    assert content == "print('hello')\n"
    assert error is None


def test_read_binary_file(tmp_path):
    f = tmp_path / "test.bin"
    f.write_bytes(b"\x00\x01\x02\x03")
    content, error = read_file(f)
    assert content is None
    assert error == "[binary file skipped]"


def test_read_latin1_file(tmp_path):
    f = tmp_path / "test.txt"
    f.write_bytes("café résumé".encode("latin-1"))
    content, error = read_file(f)
    assert content is not None
    assert error is None
    assert "caf" in content
