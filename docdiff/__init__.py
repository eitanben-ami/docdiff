"""docdiff — local docs diff against snapshots."""

__all__ = ["__version__", "Snapshot", "DocDiff", "DiffReporter"]

from docdiff.core import Snapshot, DocDiff
from docdiff.reporter import DiffReporter

__version__ = "0.1.0"
