"""Command-line entry point for MusicDNA workflows."""

from __future__ import annotations

import argparse
import sys
from typing import Sequence

from core.ingestion import IngestionError, ingest
from core.publication import PublicationError, publish_pending_results
from core.runtime import RuntimeCapabilityError


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="musicdna", description="MusicDNA command-line tools")
    commands = parser.add_subparsers(dest="command", required=True)
    add = commands.add_parser("add", help="Download one YouTube video and analyze it")
    add.add_argument("url", help="YouTube video URL")
    commands.add_parser(
        "publish-pending",
        help="Publish completed local analyses without downloading or analyzing again",
    )
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
    if arguments.command == "publish-pending":
        try:
            result = publish_pending_results()
        except PublicationError as error:
            print(f"MusicDNA publication failed: {error}")
            return 2
        print(
            "Publication: "
            f"{len(result.published)} published, {len(result.already_published)} already published, "
            f"{len(result.failed)} failed, {len(result.incomplete) + len(result.unmatched)} unmatched"
        )
        return 2 if result.has_failures else 0
    return 2


if __name__ == "__main__":
    sys.exit(main())
