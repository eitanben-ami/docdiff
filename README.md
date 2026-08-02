# docdiff

Docs diff against snapshots — added, removed, and modified detection for Markdown/HTML docs trees.

Repository: https://github.com/eitanben-ami/docdiff

## About

Documentation drift is hard to notice until it hurts users. `docdiff` gives contributors and maintainers a fast, reproducible way to compare two local docs trees and see exactly what changed: new pages, removed sections, and modified content.

Instead of relying on git history or ad-hoc `diff`, `docdiff` snapshots two directories, hashes every file, and emits a structured report listing changes with old and new SHA256 digests. It works on plain filesystems, works in CI, and needs no network.

## Features

- Snapshot any docs tree into stable file manifests.
- Diff two snapshots and list `added`, `removed`, and `modified` files.
- Emit reports in `text` or `json` format.
- Write reports to `--output` files for CI, changelogs, or PR reviews.
- Pure stdlib; no network, no external services.
- Fast recursive file discovery with deterministic sorted output.

## Installation

```bash
python -m pip install -e .
```

## Usage

```bash
# diff current docs against another directory
docdiff /path/to/docs --old /path/to/old-docs

# human-readable report to stdout
docdiff /path/to/docs --old /path/to/old-docs --format text

# machine-readable report to file
docdiff /path/to/docs --old /path/to/old-docs --format json --output report.json

# inspect current docs only
docdiff /path/to/docs
```

## Project Structure

```
docdiff/
  docdiff/
    __init__.py
    __main__.py
    cli.py
    core.py
    reporter.py
  tests/
    __init__.py
    test_docdiff.py
  docs/
    usage.md
  pyproject.toml
  README.md
```

## Tech Stack

- Python 3.10+
- `argparse` CLI
- `setuptools` packaging
- `pytest` testing
- Flat package layout

## Tags / Keywords

docs, diff, snapshot, cli, markdown, html, changelog, git-like, local-first
