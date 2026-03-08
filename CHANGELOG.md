# Changelog

All notable changes to this project will be documented in this file.

## [0.2.0] - 2026-03-08

### Added

- LLM support / OpenAI API compatible support

## [0.1.0] - 2026-03-05

### Added

- Initial release
- Directory tree rendering with box-drawing characters
- File contents output with syntax-highlighted fenced code blocks
- Markdown, plain text, and JSON output formats
- `.gitignore` support via `pathspec`
- Include/exclude filters by extension and glob pattern
- Depth limiting
- File size limits with human-readable sizes (`1mb`, `500kb`)
- Clipboard support (macOS, Linux, Windows)
- Prepend/append text or file contents (`@filepath` syntax)
- Line numbers
- Stats (file count, lines, estimated tokens)
- Project-level config via `.dumpcat.toml` with named profiles
- Symlink following with loop detection
- Hidden file support
