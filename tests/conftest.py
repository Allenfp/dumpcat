import pytest


@pytest.fixture
def tmp_project(tmp_path):
    """Create a temporary project directory with sample files."""
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "main.py").write_text("import sys\n\ndef main():\n    print('hello')\n")
    (tmp_path / "src" / "utils").mkdir()
    (tmp_path / "src" / "utils" / "helpers.py").write_text("def helper():\n    return 42\n")
    (tmp_path / "README.md").write_text("# Test Project\n")
    (tmp_path / "setup.py").write_text("from setuptools import setup\nsetup()\n")
    return tmp_path


@pytest.fixture
def tmp_project_with_gitignore(tmp_project):
    """A project with a .gitignore file."""
    (tmp_project / ".gitignore").write_text("*.pyc\n__pycache__/\nbuild/\n")
    (tmp_project / "__pycache__").mkdir()
    (tmp_project / "__pycache__" / "main.cpython-311.pyc").write_bytes(b"\x00" * 100)
    (tmp_project / "build").mkdir()
    (tmp_project / "build" / "output.txt").write_text("built")
    return tmp_project


@pytest.fixture
def tmp_project_with_config(tmp_project):
    """A project with a .dumpcat.toml config file."""
    (tmp_project / ".dumpcat.toml").write_text(
        '[default]\nformat = "plain"\nexclude = ["__pycache__"]\n\n'
        '[profiles.python]\ninclude = [".py"]\n'
    )
    return tmp_project
