"""Tests for docdiff engine and CLI."""

from __future__ import annotations

import json
import shutil
from pathlib import Path

import pytest

from docdiff.cli import build_parser, main
from docdiff.core import DocDiff, Snapshot, build_snapshot


def make_snapshot(root: Path, tree: dict[str, str]) -> dict[str, Snapshot]:
    snapshots: dict[str, Snapshot] = {}
    for name, content in tree.items():
        path = root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        snapshots[name] = Snapshot.from_path(path, root)
    return snapshots


def test_empty_snapshots_are_empty():
    assert DocDiff({}, {}).diff() == []


def test_added_file_appears():
    root = Path("/tmp/docdiff-added")
    shutil.rmtree(root, ignore_errors=True)
    root.mkdir(parents=True, exist_ok=True)
    try:
        old = make_snapshot(root / "old", {"README.md": "hello\n"})
        new = make_snapshot(root / "new", {"README.md": "hello\n", "EXTRA.md": "extra\n"})
        events = DocDiff(old, new).diff()
        assert [e["type"] for e in events] == ["added"]
        assert events[0]["path"] == "EXTRA.md"
        assert events[0]["new_sha256"] == new["EXTRA.md"].sha256
    finally:
        shutil.rmtree(root, ignore_errors=True)


def test_removed_and_modified_detected():
    root = Path("/tmp/docdiff-removed-modified")
    shutil.rmtree(root, ignore_errors=True)
    root.mkdir(parents=True, exist_ok=True)
    try:
        old = make_snapshot(root / "old", {"a.md": "v1\n", "b.md": "v1\n"})
        new = make_snapshot(root / "new", {"a.md": "v2\n"})
        events = DocDiff(old, new).diff()
        assert {event["type"] for event in events} == {"modified", "removed"}
        assert any(event["path"] == "a.md" and event["type"] == "modified" for event in events)
    finally:
        shutil.rmtree(root, ignore_errors=True)


def test_identical_snapshots_produce_no_events():
    root = Path("/tmp/docdiff-same")
    shutil.rmtree(root, ignore_errors=True)
    root.mkdir(parents=True, exist_ok=True)
    try:
        snapshots = make_snapshot(root, {"f.md": "c\n", "sub/g.md": "h\n"})
        assert DocDiff(snapshots, snapshots).diff() == []
    finally:
        shutil.rmtree(root, ignore_errors=True)


def test_build_snapshot_rejects_dangling_symlinks():
    root = Path("/tmp/docdiff-symlink")
    shutil.rmtree(root, ignore_errors=True)
    root.mkdir(parents=True, exist_ok=True)
    try:
        link = root / "dangling-link"
        target = root / "missing"
        try:
            link.symlink_to(target)
        except OSError:
            pytest.skip("symlinks not available")
        assert "dangling-link" not in build_snapshot(root)
    finally:
        shutil.rmtree(root, ignore_errors=True)


def test_main_missing_path_returns_nonzero():
    rc = main(["/root/this-path-does-not-exist"])
    assert rc == 1


def test_help_exits_zero():
    parser = build_parser()
    with pytest.raises(SystemExit) as exc:
        parser.parse_args(["--help"])
    assert exc.value.code == 0


def test_cli_text_report_contains_expected_line(tmp_path: Path):
    old = tmp_path / "old"
    new = tmp_path / "new"
    old.mkdir(parents=True, exist_ok=True)
    new.mkdir(parents=True, exist_ok=True)
    old_snapshot = make_snapshot(old, {"README.md": "once"})
    new_snapshot = make_snapshot(new, {"README.md": "twice"})
    output = tmp_path / "report.txt"
    assert main([str(new), "--old", str(old), "--format", "text", "--output", str(output)]) == 0
    text = output.read_text(encoding="utf-8")
    assert text.startswith("modified: README.md ")
    assert old_snapshot["README.md"].sha256 in text
    assert new_snapshot["README.md"].sha256 in text


def test_cli_json_report_is_valid(tmp_path: Path):
    old = tmp_path / "old"
    new = tmp_path / "new"
    old.mkdir(parents=True, exist_ok=True)
    new.mkdir(parents=True, exist_ok=True)
    make_snapshot(old, {})
    new_snapshot = make_snapshot(new, {"NEW.md": "new"})
    output = tmp_path / "report.json"
    assert main([str(new), "--old", str(old), "--format", "json", "--output", str(output)]) == 0
    parsed = json.loads(output.read_text(encoding="utf-8"))
    change = parsed["changes"][0]
    assert change["type"] == "added"
    assert change["path"] == "NEW.md"
    assert change["new_sha256"] == new_snapshot["NEW.md"].sha256
