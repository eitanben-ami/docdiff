"""Core snapshot and diff engine for docdiff."""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List


@dataclass(frozen=True)
class Snapshot:
    """Immutable snapshot of a docs tree entry."""

    path: str
    sha256: str

    @staticmethod
    def hash_bytes(data: bytes) -> str:
        return hashlib.sha256(data).hexdigest()

    @classmethod
    def from_path(cls, file_path: Path, root: Path) -> Snapshot:
        rel = file_path.relative_to(root)
        data = file_path.read_bytes()
        return cls(path=str(rel), sha256=cls.hash_bytes(data))


def _collect(path: Path) -> List[Path]:
    if path.is_file():
        return [path]
    return sorted(p for p in path.rglob("*") if p.is_file())


def build_snapshot(root: Path) -> dict[str, Snapshot]:
    snapshots: dict[str, Snapshot] = {}
    for file_path in _collect(root):
        snapshots[str(file_path.relative_to(root))] = Snapshot.from_path(file_path, root)
    return snapshots


class DocDiff:
    """Pairwise diff between two docs snapshots."""

    def __init__(
        self,
        old_snapshot: dict[str, Snapshot],
        new_snapshot: dict[str, Snapshot],
    ) -> None:
        self.old_snapshot = old_snapshot
        self.new_snapshot = new_snapshot

    def diff(self) -> list[dict[str, str]]:
        """Return change events sorted by path."""
        events: list[dict[str, str]] = []
        old_paths = set(self.old_snapshot)
        new_paths = set(self.new_snapshot)

        events.extend(
            {
                "type": "added",
                "path": p,
                "old_sha256": "",
                "new_sha256": self.new_snapshot[p].sha256,
            }
            for p in sorted(new_paths - old_paths)
        )

        events.extend(
            {
                "type": "removed",
                "path": p,
                "old_sha256": self.old_snapshot[p].sha256,
                "new_sha256": "",
            }
            for p in sorted(old_paths - new_paths)
        )

        events.extend(
            {
                "type": "modified",
                "path": p,
                "old_sha256": self.old_snapshot[p].sha256,
                "new_sha256": self.new_snapshot[p].sha256,
            }
            for p in sorted(old_paths & new_paths)
            if self.old_snapshot[p].sha256 != self.new_snapshot[p].sha256
        )

        return events
