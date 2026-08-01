# docdiff Usage

## Quick Start
```bash
docdiff /path/to/docs
```

## Against a Previous Snapshot
```bash
docdiff /path/to/docs --old /path/to/old-docs
```

## Output Formats
- `--format text` — human-readable change list.
- `--format json` — machine-readable report with `path`, `old_sha256`, and `new_sha256` fields.

## Write Report to File
```bash
docdiff /path/to/docs --old /path/to/old-docs --format json --output report.json
```

## Common Workflows
1. Snapshot a stable docs tree as a baseline.
2. Make documentation changes.
3. Run `docdiff` against the baseline to see what changed.
4. Commit the report alongside the diff for changelog review.
