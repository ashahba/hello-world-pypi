"""Entry point for the ``hello-world`` console script."""

from __future__ import annotations

import argparse
from collections.abc import Sequence

from . import __version__, hello


def main(argv: Sequence[str] | None = None) -> int:
    """Print a greeting. Returns a process exit code."""
    parser = argparse.ArgumentParser(prog="hello-world", description="Print a greeting.")
    parser.add_argument("name", nargs="?", default="World", help="who to greet")
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    args = parser.parse_args(argv)
    print(hello(args.name))
    return 0
