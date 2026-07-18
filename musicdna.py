"""Command-line entry point for MusicDNA workflows."""

from __future__ import annotations

import argparse
import sys
from typing import Sequence

from core.ingestion import IngestionError, ingest
from core.runtime import RuntimeCapabilityError


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="musicdna", description="MusicDNA command-line tools")
    commands = parser.add_subparsers(dest="command", required=True)
    add = commands.add_parser("add", help="Download one YouTube video and analyze it")
    add.add_argument("url", help="YouTube video URL")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    arguments = build_parser().parse_args(argv)
    if arguments.command == "add":
        try:
            result = ingest(arguments.url)
        except (IngestionError, RuntimeCapabilityError) as error:
            print(f"MusicDNA add failed: {error}")
            return 2
        print(f"Status: {result.status}")
        if result.report_path:
            print(f"Summary: {result.report_path}")
        return 0
    return 2


if __name__ == "__main__":
    sys.exit(main())
