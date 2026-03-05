from __future__ import annotations

import argparse

from . import __version__
from .core import run


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="dumpcat",
        description="Dump a directory's file tree and contents into a single formatted output.",
    )
    parser.add_argument("path", nargs="?", default=".", help="Directory to dump (default: .)")
    parser.add_argument("-V", "--version", action="version", version=f"%(prog)s {__version__}")

    parser.add_argument("-o", "--output", type=str, default=None, help="Output file path")
    parser.add_argument("-c", "--clipboard", action="store_true", help="Copy output to clipboard")
    parser.add_argument("-d", "--depth", type=int, default=None, help="Max directory depth")
    parser.add_argument(
        "-i", "--include", action="append", default=None,
        help="Include only these extensions (e.g. -i .py -i .js)",
    )
    parser.add_argument(
        "-e", "--exclude", action="append", default=None,
        help="Exclude glob patterns (e.g. -e node_modules -e '*.pyc')",
    )
    gitignore_group = parser.add_mutually_exclusive_group()
    gitignore_group.add_argument(
        "--gitignore", action="store_true", dest="gitignore", default=True,
        help="Respect .gitignore rules (default: true)",
    )
    gitignore_group.add_argument(
        "--no-gitignore", action="store_false", dest="gitignore",
        help="Ignore .gitignore rules",
    )
    parser.add_argument("--tree-only", action="store_true", help="Only show tree, no file contents")
    parser.add_argument("--no-tree", action="store_true", help="Only show file contents, no tree")
    parser.add_argument(
        "-p", "--prepend", type=str, default=None,
        help="Text or @filepath to prepend to output",
    )
    parser.add_argument(
        "-a", "--append", type=str, default=None,
        help="Text or @filepath to append to output",
    )
    parser.add_argument(
        "--max-size", type=str, default="1mb",
        help="Skip files larger than this (default: 1mb)",
    )
    parser.add_argument("-s", "--stats", action="store_true", help="Show file count, lines, est. tokens")
    parser.add_argument(
        "-f", "--format", choices=["markdown", "plain", "json"], default="markdown",
        help="Output format (default: markdown)",
    )
    parser.add_argument("--config", type=str, default=None, help="Path to config file")
    parser.add_argument("--profile", type=str, default="default", help="Named profile from config")
    parser.add_argument("--follow-symlinks", action="store_true", help="Follow symbolic links")
    parser.add_argument("--hidden", action="store_true", help="Include dotfiles/dotdirs")
    parser.add_argument("-n", "--line-numbers", action="store_true", help="Add line numbers to content")

    return parser


def main(argv: list[str] | None = None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.tree_only and args.no_tree:
        parser.error("--tree-only and --no-tree are mutually exclusive")

    run(args)


if __name__ == "__main__":
    main()
