"""DocDiff CLI — compare two docs tree snapshots."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from docdiff.core import DocDiff, build_snapshot
from docdiff.reporter import DiffReporter


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="docdiff",
        description="Diff local docs tree against a previous snapshot.",
    )
    parser.add_argument("directory", help="docs directory to inspect")
    parser.add_argument("--old", required=False, help="previous snapshot directory")
    parser.add_argument(
        "--format",
        choices=["text", "json"],
        default="text",
        help="output format",
    )
    parser.add_argument(
        "--output",
        required=False,
        help="write report to file instead of stdout",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    target = Path(args.directory)

    if not target.exists() or not target.is_dir():
        print(f"error: '{target}' is not a directory", file=sys.stderr)
        return 1

    new_snapshot = build_snapshot(target)
    old_snapshot = build_snapshot(Path(args.old)) if args.old else {}

    diff = DocDiff(old_snapshot, new_snapshot)
    events = diff.diff()
    reporter = DiffReporter(events)

    output = Path(args.output) if args.output else None
    if output:
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(reporter.to_json() if args.format == "json" else reporter.to_text())
    else:
        reporter.write(sys.stdout, args.format)

    return 0


from docdiff.core import DocDiff  # noqa: E402

if __name__ == "__main__":
    raise SystemExit(main())
