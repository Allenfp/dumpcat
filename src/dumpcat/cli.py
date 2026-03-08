from __future__ import annotations

import argparse
import sys

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
    parser.add_argument("-A", "--output-append", action="store_true", help="Append to output file instead of overwriting")
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

    parser.add_argument("-v", "--verbose", action="store_true", help="Print verbose logs to stderr")

    llm_group = parser.add_argument_group("LLM options")
    llm_group.add_argument(
        "--llm", nargs="?", const=True, default=None, metavar="PROVIDER_OR_URL",
        help="Send output to an LLM. Value: ollama, vllm, lmstudio, a URL, or omit for default target",
    )
    llm_group.add_argument(
        "-t", "--target", type=str, default=None, metavar="NAME",
        help="Named LLM target from config [llm.targets.*]",
    )
    llm_group.add_argument(
        "-m", "--model", type=str, default=None, metavar="NAME",
        help="LLM model name (e.g. llama3, gpt-4o)",
    )
    llm_group.add_argument(
        "--system-prompt", type=str, default=None, metavar="TEXT",
        help="System prompt for the LLM",
    )
    llm_group.add_argument(
        "--set", action="append", default=None, metavar="KEY=VALUE",
        help="LLM parameter (repeatable): --set temperature=0.7 --set max_tokens=4096",
    )
    llm_group.add_argument(
        "--api-key", type=str, default=None, metavar="KEY",
        help="API key for the endpoint",
    )

    return parser


def main(argv: list[str] | None = None) -> None:
    # Handle init subcommand before argparse
    raw = argv if argv is not None else sys.argv[1:]
    if raw and raw[0] == "init":
        from .init import run_init
        run_init(raw[1:])
        return

    parser = build_parser()
    args = parser.parse_args(argv)

    if args.tree_only and args.no_tree:
        parser.error("--tree-only and --no-tree are mutually exclusive")

    run(args)


if __name__ == "__main__":
    main()
