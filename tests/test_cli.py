import json

from dumpcat.cli import main


def test_basic_run(tmp_project, capsys):
    main([str(tmp_project)])
    captured = capsys.readouterr()
    assert "# File Tree" in captured.out
    assert "main.py" in captured.out
    assert "helpers.py" in captured.out


def test_plain_format(tmp_project, capsys):
    main(["-f", "plain", str(tmp_project)])
    captured = capsys.readouterr()
    assert "=== TREE ===" in captured.out
    assert "=== src/main.py ===" in captured.out


def test_json_format(tmp_project, capsys):
    main(["-f", "json", str(tmp_project)])
    captured = capsys.readouterr()
    data = json.loads(captured.out)
    assert "tree" in data
    assert "files" in data


def test_include_filter(tmp_project, capsys):
    main(["-i", ".py", str(tmp_project)])
    captured = capsys.readouterr()
    assert "main.py" in captured.out
    assert "README.md" not in captured.out.split("# File Contents")[-1]


def test_exclude_filter(tmp_project, capsys):
    main(["-e", "*.md", str(tmp_project)])
    captured = capsys.readouterr()
    content_section = captured.out.split("# File Contents")[-1] if "# File Contents" in captured.out else captured.out
    assert "README.md" not in content_section


def test_depth_limit(tmp_project, capsys):
    main(["-d", "0", str(tmp_project)])
    captured = capsys.readouterr()
    assert "helpers.py" not in captured.out


def test_tree_only(tmp_project, capsys):
    main(["--tree-only", str(tmp_project)])
    captured = capsys.readouterr()
    assert "# File Tree" in captured.out
    assert "# File Contents" not in captured.out


def test_no_tree(tmp_project, capsys):
    main(["--no-tree", str(tmp_project)])
    captured = capsys.readouterr()
    assert "# File Tree" not in captured.out
    assert "# File Contents" in captured.out


def test_stats(tmp_project, capsys):
    main(["-s", str(tmp_project)])
    captured = capsys.readouterr()
    assert "# Stats" in captured.out
    assert "Files:" in captured.out


def test_output_file(tmp_project, capsys):
    output = tmp_project / "output.md"
    main(["-o", str(output), str(tmp_project)])
    assert output.exists()
    content = output.read_text()
    assert "# File Tree" in content
    # output file should not be in the dump itself
    assert "output.md" not in content.split("# File Contents")[-1]


def test_line_numbers(tmp_project, capsys):
    main(["-n", "-i", ".py", str(tmp_project)])
    captured = capsys.readouterr()
    assert "1 | " in captured.out


def test_prepend_text(tmp_project, capsys):
    main(["-p", "Review this code", str(tmp_project)])
    captured = capsys.readouterr()
    assert captured.out.startswith("Review this code")


def test_prepend_file(tmp_project, capsys):
    prompt_file = tmp_project / "prompt.txt"
    prompt_file.write_text("Please analyze this codebase")
    main(["-p", f"@{prompt_file}", str(tmp_project)])
    captured = capsys.readouterr()
    assert "Please analyze this codebase" in captured.out


def test_gitignore_respected(tmp_project_with_gitignore, capsys):
    main([str(tmp_project_with_gitignore)])
    captured = capsys.readouterr()
    assert "__pycache__" not in captured.out
    assert "build" not in captured.out


def test_gitignore_disabled(tmp_project_with_gitignore, capsys):
    main(["--no-gitignore", str(tmp_project_with_gitignore)])
    captured = capsys.readouterr()
    assert "build/" in captured.out or "build" in captured.out


def test_config_profile(tmp_project_with_config, capsys):
    main(["--profile", "python", str(tmp_project_with_config)])
    captured = capsys.readouterr()
    # python profile includes only .py files
    content_part = captured.out.split("# File Contents")[-1] if "# File Contents" in captured.out else ""
    assert "README.md" not in content_part
    assert "main.py" in captured.out
