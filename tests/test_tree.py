from dumpcat.tree import render_tree


def test_render_tree():
    entries = [
        {"path": "src", "is_dir": True},
        {"path": "src/main.py", "is_dir": False},
        {"path": "src/utils", "is_dir": True},
        {"path": "src/utils/helpers.py", "is_dir": False},
        {"path": "README.md", "is_dir": False},
    ]
    result = render_tree(entries)
    lines = result.split("\n")
    assert lines[0] == "."
    assert "├── src/" in lines
    assert "│   └── main.py" in lines or "│   ├── main.py" in lines
    assert "│   ├── utils/" in lines or "│   └── utils/" in lines
    assert "└── README.md" in lines


def test_render_empty_tree():
    assert render_tree([]) == "."
