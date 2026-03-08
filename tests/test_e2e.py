"""End-to-end tests for dumpcat CLI.

Tests multi-flag combinations, LLM integration (mocked), and edge cases
by invoking the CLI entry point dumpcat.cli.main(argv).
"""

from __future__ import annotations

import json
from unittest.mock import MagicMock

import pytest

from dumpcat.cli import main


# ── Helpers ───────────────────────────────────────────────


def _mock_urlopen(monkeypatch, content="LLM response", prompt_tokens=100, completion_tokens=50):
    """Set up a mocked urllib.request.urlopen that returns a valid LLM response."""
    response_body = json.dumps({
        "choices": [{"message": {"content": content}}],
        "usage": {"prompt_tokens": prompt_tokens, "completion_tokens": completion_tokens},
    }).encode()
    mock_resp = MagicMock()
    mock_resp.read.return_value = response_body
    mock_resp.__enter__ = lambda s: s
    mock_resp.__exit__ = MagicMock(return_value=False)
    monkeypatch.setattr("urllib.request.urlopen", lambda req, timeout=None: mock_resp)
    return mock_resp


# ── 1. Multi-flag combinations ───────────────────────────


class TestMultiFlagCombinations:
    """Tests that exercise multiple CLI flags together."""

    def test_json_include_depth_stats_linenumbers(self, tmp_project, capsys):
        """-f json -i .py -d 1 -s -n"""
        main(["-f", "json", "-i", ".py", "-d", "1", "-s", "-n", str(tmp_project)])
        captured = capsys.readouterr()
        data = json.loads(captured.out)
        assert "tree" in data
        assert "files" in data
        assert "stats" in data
        # JSON files is a dict keyed by path
        file_paths = list(data["files"].keys())
        # depth 1: helpers.py is at depth 2 (src/utils/helpers.py), should be excluded
        assert "src/utils/helpers.py" not in file_paths
        # only .py files
        for p in file_paths:
            assert p.endswith(".py")
        # line numbers should be present in content
        for p, info in data["files"].items():
            if "content" in info:
                assert "1 | " in info["content"]

    def test_plain_include_exclude_stats(self, tmp_project, capsys):
        """-f plain -i .py -e "*.md" -s"""
        main(["-f", "plain", "-i", ".py", "-e", "*.md", "-s", str(tmp_project)])
        captured = capsys.readouterr()
        assert "=== TREE ===" in captured.out
        assert "README.md" not in captured.out
        # Only .py files in content sections
        assert "=== src/main.py ===" in captured.out
        assert "Stats" in captured.out or "Files:" in captured.out

    def test_tree_only_exclude_depth0(self, tmp_project, capsys):
        """--tree-only -e "*.md" -d 0"""
        main(["--tree-only", "-e", "*.md", "-d", "0", str(tmp_project)])
        captured = capsys.readouterr()
        # tree only: no file contents section
        assert "# File Contents" not in captured.out
        # README.md excluded
        assert "README.md" not in captured.out
        # depth 0: no subdirectory files
        assert "helpers.py" not in captured.out

    def test_no_tree_linenumbers_include_stats(self, tmp_project, capsys):
        """--no-tree -n -i .py -s"""
        main(["--no-tree", "-n", "-i", ".py", "-s", str(tmp_project)])
        captured = capsys.readouterr()
        assert "# File Tree" not in captured.out
        assert "=== TREE ===" not in captured.out
        # line numbers present
        assert "1 | " in captured.out
        # only .py files
        assert "README.md" not in captured.out

    def test_output_file_with_include(self, tmp_project, capsys):
        """-o file.md -i .py"""
        output_file = tmp_project / "output.md"
        main(["-o", str(output_file), "-i", ".py", str(tmp_project)])
        assert output_file.exists()
        content = output_file.read_text()
        assert "main.py" in content
        # .md files should not appear in file contents
        contents_section = content.split("# File Contents")[-1] if "# File Contents" in content else content
        assert "README.md" not in contents_section
        # stderr confirms write
        captured = capsys.readouterr()
        assert "Output written to" in captured.err

    def test_prepend_append_plain(self, tmp_project, capsys):
        """-p "Review this" -a "End of dump" -f plain"""
        main(["-p", "Review this", "-a", "End of dump", "-f", "plain", str(tmp_project)])
        captured = capsys.readouterr()
        assert captured.out.startswith("Review this")
        assert captured.out.rstrip().endswith("End of dump")

    def test_prepend_append_markdown(self, tmp_project, capsys):
        """-p "HEADER" -a "FOOTER" -f markdown"""
        main(["-p", "HEADER", "-a", "FOOTER", "-f", "markdown", str(tmp_project)])
        captured = capsys.readouterr()
        assert captured.out.startswith("HEADER")
        assert captured.out.rstrip().endswith("FOOTER")

    def test_prepend_append_json(self, tmp_project, capsys):
        """-p "PREFIX" -a "SUFFIX" -f json"""
        main(["-p", "PREFIX", "-a", "SUFFIX", "-f", "json", str(tmp_project)])
        captured = capsys.readouterr()
        data = json.loads(captured.out)
        assert data.get("prepend") == "PREFIX"
        assert data.get("append") == "SUFFIX"

    def test_no_gitignore_hidden_depth(self, tmp_project_with_gitignore, capsys):
        """--no-gitignore --hidden -d 2"""
        main(["--no-gitignore", "--hidden", "-d", "2", str(tmp_project_with_gitignore)])
        captured = capsys.readouterr()
        # With --no-gitignore, build/ should appear
        assert "build" in captured.out
        # With --hidden, .gitignore should appear
        assert ".gitignore" in captured.out

    def test_config_profile_with_format_override(self, tmp_project_with_config, capsys):
        """--profile python -f json"""
        main(["--profile", "python", "-f", "json", str(tmp_project_with_config)])
        captured = capsys.readouterr()
        data = json.loads(captured.out)
        # python profile includes only .py files
        file_paths = list(data["files"].keys())
        for p in file_paths:
            assert p.endswith(".py"), f"Expected only .py files, got {p}"
        assert any("main.py" in p for p in file_paths)

    def test_line_numbers_plain(self, tmp_project, capsys):
        """-n -f plain"""
        main(["-n", "-f", "plain", "-i", ".py", str(tmp_project)])
        captured = capsys.readouterr()
        assert "=== TREE ===" in captured.out
        assert "1 | " in captured.out

    def test_line_numbers_json(self, tmp_project, capsys):
        """-n -f json"""
        main(["-n", "-f", "json", "-i", ".py", str(tmp_project)])
        captured = capsys.readouterr()
        data = json.loads(captured.out)
        for p, info in data["files"].items():
            if "content" in info:
                assert "1 | " in info["content"]

    @pytest.mark.parametrize("fmt,tree_marker,stats_marker", [
        ("markdown", "# File Tree", "# Stats"),
        ("plain", "=== TREE ===", "=== STATS ==="),
        ("json", None, None),  # handled separately
    ])
    def test_stats_in_all_formats(self, tmp_project, capsys, fmt, tree_marker, stats_marker):
        """-s -f <format>"""
        main(["-s", "-f", fmt, str(tmp_project)])
        captured = capsys.readouterr()
        if fmt == "json":
            data = json.loads(captured.out)
            assert "stats" in data
            assert "files" in data["stats"] or "est_tokens" in data["stats"]
        else:
            assert tree_marker in captured.out
            assert stats_marker in captured.out

    def test_multiple_includes(self, tmp_project, capsys):
        """-i .py -i .md"""
        main(["-i", ".py", "-i", ".md", str(tmp_project)])
        captured = capsys.readouterr()
        assert "main.py" in captured.out
        assert "README.md" in captured.out
        # setup.py is .py so it should be included
        assert "setup.py" in captured.out

    def test_multiple_excludes(self, tmp_project, capsys):
        """-e "*.py" -e "*.md" """
        main(["-e", "*.py", "-e", "*.md", str(tmp_project)])
        captured = capsys.readouterr()
        contents_section = captured.out.split("# File Contents")[-1] if "# File Contents" in captured.out else captured.out
        assert "main.py" not in contents_section
        assert "README.md" not in contents_section
        assert "setup.py" not in contents_section

    def test_max_size_with_filters(self, tmp_project, capsys):
        """--max-size 10 -i .py  (files >10 bytes should be skipped)"""
        # main.py content is "import sys\n\ndef main():\n    print('hello')\n" = well over 10 bytes
        main(["--max-size", "10", "-i", ".py", str(tmp_project)])
        captured = capsys.readouterr()
        # With max-size 10, all .py files are larger than 10 bytes, so none should appear
        contents_section = captured.out.split("# File Contents")[-1] if "# File Contents" in captured.out else captured.out
        assert "import sys" not in contents_section
        assert "def helper" not in contents_section

    def test_kitchen_sink(self, tmp_project, capsys):
        """-f json -i .py -d 2 -s -n -p "Start" -a "End" """
        main(["-f", "json", "-i", ".py", "-d", "2", "-s", "-n",
              "-p", "Start", "-a", "End", str(tmp_project)])
        captured = capsys.readouterr()
        data = json.loads(captured.out)
        assert data.get("prepend") == "Start"
        assert data.get("append") == "End"
        assert "stats" in data
        assert "files" in data
        assert "tree" in data
        # only .py files (JSON files is a dict keyed by path)
        for p in data["files"]:
            assert p.endswith(".py")
        # line numbers
        for p, info in data["files"].items():
            if "content" in info:
                assert "1 | " in info["content"]


# ── 2. LLM flag combinations (all mocked) ────────────────


class TestLLMFlagCombinations:
    """Tests for --llm and related flags, with mocked HTTP."""

    def test_llm_ollama_basic(self, tmp_project, capsys, monkeypatch):
        """--llm ollama -m llama3"""
        _mock_urlopen(monkeypatch, content="LLM says hello")
        main(["--llm", "ollama", "-m", "llama3", str(tmp_project)])
        captured = capsys.readouterr()
        # stderr should have target/model/tokens info
        assert "[llm] target:" in captured.err
        assert "llama3" in captured.err
        assert "tokens" in captured.err
        # stdout should have the LLM response
        assert "LLM says hello" in captured.out

    def test_llm_lmstudio_output_file(self, tmp_project, capsys, monkeypatch):
        """--llm lmstudio -m model -o output.txt"""
        _mock_urlopen(monkeypatch, content="File response content")
        output_file = tmp_project / "llm_output.txt"
        main(["--llm", "lmstudio", "-m", "model", "-o", str(output_file), str(tmp_project)])
        assert output_file.exists()
        content = output_file.read_text()
        assert "File response content" in content
        captured = capsys.readouterr()
        assert "Response written to" in captured.err

    def test_llm_target_from_config(self, tmp_project, capsys, monkeypatch):
        """--llm -t targetname with mocked config"""
        fake_config = {
            "targets": {
                "mylocal": {
                    "provider": "ollama",
                    "model": "mistral",
                }
            }
        }
        monkeypatch.setattr("dumpcat.llm.load_llm_config", lambda: fake_config)
        _mock_urlopen(monkeypatch, content="Config target response")
        main(["--llm", "-t", "mylocal", str(tmp_project)])
        captured = capsys.readouterr()
        assert "Config target response" in captured.out
        assert "mylocal" in captured.err

    def test_llm_with_filters_and_stats(self, tmp_project, capsys, monkeypatch):
        """--llm ollama -m llama3 -i .py -s"""
        _mock_urlopen(monkeypatch, content="Filtered LLM response")
        main(["--llm", "ollama", "-m", "llama3", "-i", ".py", "-s", str(tmp_project)])
        captured = capsys.readouterr()
        assert "Filtered LLM response" in captured.out

    def test_llm_with_system_prompt(self, tmp_project, capsys, monkeypatch):
        """--llm ollama -m llama3 --system-prompt "Be brief" """
        captured_req = {}
        response_body = json.dumps({
            "choices": [{"message": {"content": "Brief response"}}],
            "usage": {"prompt_tokens": 100, "completion_tokens": 50},
        }).encode()
        mock_resp = MagicMock()
        mock_resp.read.return_value = response_body
        mock_resp.__enter__ = lambda s: s
        mock_resp.__exit__ = MagicMock(return_value=False)

        def capture_urlopen(req, timeout=None):
            captured_req["data"] = json.loads(req.data.decode())
            return mock_resp

        monkeypatch.setattr("urllib.request.urlopen", capture_urlopen)
        main(["--llm", "ollama", "-m", "llama3", "--system-prompt", "Be brief", str(tmp_project)])
        captured = capsys.readouterr()
        assert "Brief response" in captured.out
        # Verify system prompt was in the request payload
        messages = captured_req["data"]["messages"]
        system_msgs = [m for m in messages if m["role"] == "system"]
        assert len(system_msgs) == 1
        assert system_msgs[0]["content"] == "Be brief"

    def test_llm_with_set_params(self, tmp_project, capsys, monkeypatch):
        """--llm ollama -m llama3 --set temperature=0.5"""
        captured_req = {}
        response_body = json.dumps({
            "choices": [{"message": {"content": "Param response"}}],
            "usage": {"prompt_tokens": 100, "completion_tokens": 50},
        }).encode()
        mock_resp = MagicMock()
        mock_resp.read.return_value = response_body
        mock_resp.__enter__ = lambda s: s
        mock_resp.__exit__ = MagicMock(return_value=False)

        def capture_urlopen(req, timeout=None):
            captured_req["data"] = json.loads(req.data.decode())
            return mock_resp

        monkeypatch.setattr("urllib.request.urlopen", capture_urlopen)
        main(["--llm", "ollama", "-m", "llama3", "--set", "temperature=0.5", str(tmp_project)])
        captured = capsys.readouterr()
        assert "Param response" in captured.out
        # Verify temperature was passed in payload
        assert captured_req["data"]["temperature"] == 0.5

    def test_llm_no_target_no_default_error(self, tmp_project, capsys, monkeypatch):
        """--llm with no provider and no default target should error."""
        monkeypatch.setattr("dumpcat.llm.load_llm_config", lambda: {})
        # --llm with no value sets args.llm=True (nargs="?", const=True)
        # To avoid --llm consuming the path as its value, put path first
        with pytest.raises(SystemExit):
            main([str(tmp_project), "--llm"])
        captured = capsys.readouterr()
        assert "No --llm value and no default_target" in captured.err

    def test_llm_no_model_error(self, tmp_project, capsys, monkeypatch):
        """--llm ollama without -m should error with 'No model specified'."""
        with pytest.raises(SystemExit):
            main(["--llm", "ollama", str(tmp_project)])
        captured = capsys.readouterr()
        assert "No model specified" in captured.err


# ── 3. Edge cases ────────────────────────────────────────


class TestEdgeCases:

    def test_tree_only_and_no_tree_mutually_exclusive(self, tmp_project):
        """--tree-only --no-tree should cause a SystemExit error."""
        with pytest.raises(SystemExit):
            main(["--tree-only", "--no-tree", str(tmp_project)])

    def test_empty_directory(self, tmp_path, capsys):
        """An empty directory should produce valid output with no files."""
        main([str(tmp_path)])
        captured = capsys.readouterr()
        # Should not crash; output should be valid
        assert captured.out is not None

    def test_empty_directory_json(self, tmp_path, capsys):
        """An empty directory in JSON format should produce valid JSON."""
        main(["-f", "json", str(tmp_path)])
        captured = capsys.readouterr()
        data = json.loads(captured.out)
        assert data["files"] == {}

    def test_all_files_exceed_max_size(self, tmp_path, capsys):
        """When all files exceed --max-size, output should have no file contents."""
        # Create files that are larger than 5 bytes
        (tmp_path / "big.py").write_text("x" * 100)
        (tmp_path / "huge.txt").write_text("y" * 200)
        main(["--max-size", "5", "-f", "json", str(tmp_path)])
        captured = capsys.readouterr()
        data = json.loads(captured.out)
        # No files should appear (all exceed max-size)
        assert data["files"] == {}

    def test_empty_directory_plain(self, tmp_path, capsys):
        """An empty directory in plain format."""
        main(["-f", "plain", str(tmp_path)])
        captured = capsys.readouterr()
        assert captured.out is not None

    def test_prepend_from_file(self, tmp_project, capsys):
        """Prepend from a @file reference."""
        prompt_file = tmp_project / "prompt.txt"
        prompt_file.write_text("Analyze the following code:")
        main(["-p", f"@{prompt_file}", "-f", "plain", str(tmp_project)])
        captured = capsys.readouterr()
        assert captured.out.startswith("Analyze the following code:")

    def test_append_from_file(self, tmp_project, capsys):
        """Append from a @file reference."""
        footer_file = tmp_project / "footer.txt"
        footer_file.write_text("END OF DUMP")
        main(["-a", f"@{footer_file}", "-f", "plain", str(tmp_project)])
        captured = capsys.readouterr()
        assert captured.out.rstrip().endswith("END OF DUMP")

    def test_depth_0_only_root_files(self, tmp_project, capsys):
        """Depth 0 should only show root-level files."""
        main(["-d", "0", "-f", "json", str(tmp_project)])
        captured = capsys.readouterr()
        data = json.loads(captured.out)
        file_paths = list(data["files"].keys())
        # Root files only, no subdirectory files
        for p in file_paths:
            assert "/" not in p, f"Depth 0 should not include {p}"

    def test_output_append_creates_new_file(self, tmp_project, capsys):
        """``-o FILE -A`` creates the file if it doesn't exist."""
        output_file = tmp_project / "new_output.md"
        main(["-o", str(output_file), "-A", "-i", ".py", str(tmp_project)])
        assert output_file.exists()
        content = output_file.read_text()
        assert "main.py" in content
        captured = capsys.readouterr()
        assert "appended to" in captured.err

    def test_output_append_adds_to_existing(self, tmp_project, capsys):
        """``-o FILE -A`` appends to an existing file rather than overwriting."""
        output_file = tmp_project / "append_output.md"
        output_file.write_text("EXISTING CONTENT\n")
        main(["-o", str(output_file), "-A", "-i", ".py", str(tmp_project)])
        content = output_file.read_text()
        assert content.startswith("EXISTING CONTENT\n")
        assert "main.py" in content
        captured = capsys.readouterr()
        assert "appended to" in captured.err

    def test_output_overwrite_replaces_existing(self, tmp_project, capsys):
        """-o FILE without -A overwrites existing content."""
        output_file = tmp_project / "overwrite_output.md"
        output_file.write_text("OLD CONTENT\n")
        main(["-o", str(output_file), "-i", ".py", str(tmp_project)])
        content = output_file.read_text()
        assert "OLD CONTENT" not in content
        assert "main.py" in content
        captured = capsys.readouterr()
        assert "written to" in captured.err

    def test_output_append_multiple_runs(self, tmp_project, capsys):
        """Multiple runs with -A accumulate output."""
        output_file = tmp_project / "multi_append.md"
        main(["-o", str(output_file), "-A", "--tree-only", str(tmp_project)])
        first_size = output_file.stat().st_size
        capsys.readouterr()
        main(["-o", str(output_file), "-A", "--tree-only", str(tmp_project)])
        second_size = output_file.stat().st_size
        assert second_size > first_size

    def test_output_file_not_included_in_dump(self, tmp_project, capsys):
        """The output file itself should be excluded from the dump."""
        output_file = tmp_project / "dump_output.md"
        main(["-o", str(output_file), "-f", "json", str(tmp_project)])
        content = output_file.read_text()
        data = json.loads(content)
        file_paths = list(data["files"].keys())
        assert "dump_output.md" not in file_paths
