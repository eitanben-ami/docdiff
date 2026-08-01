"""Reporters for docdiff events."""

from __future__ import annotations

from typing import IO, Iterable


def render_table(events: Iterable[dict[str, str]]) -> str:
    """Render diff events as a human-readable Markdown-ish table."""
    lines = ["| Type | Path | Old SHA256 | New SHA256 |", "| --- | --- | --- | --- |"]
    for event in events:
        lines.append(
            f"| {event['type']} | {event['path']} "
            f"| {event['old_sha256']} | {event['new_sha256']} |"
        )
    return "\n".join(lines) + "\n"


class DiffReporter:
    """Transform diff events into JSON or text report."""

    def __init__(self, events: list[dict[str, str]]) -> None:
        self.events = events

    def to_json(self) -> str:
        import json

        return json.dumps({"changes": self.events}, indent=2) + "\n"

    def to_text(self) -> str:
        lines: list[str] = []
        for event in self.events:
            lines.append(
                f"{event['type']}: {event['path']} "
                f"{event['old_sha256']} -> {event['new_sha256']}"
            )
        return "\n".join(lines) + "\n"

    def write(self, handle: IO[str], fmt: str) -> None:
        if fmt == "json":
            handle.write(self.to_json())
        elif fmt == "text":
            handle.write(self.to_text())
        else:
            raise ValueError(f"unknown format: {fmt}")
