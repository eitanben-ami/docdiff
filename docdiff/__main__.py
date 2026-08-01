#!/usr/bin/env python3
"""Package entrypoint shim."""

from docdiff.cli import main

if __name__ == "__main__":
    raise SystemExit(main())
