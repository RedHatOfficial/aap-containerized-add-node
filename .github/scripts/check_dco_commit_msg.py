#!/usr/bin/env python3
"""Fail if a commit message lacks a DCO Signed-off-by trailer.

Usage:
  python3 .github/scripts/check_dco_commit_msg.py .git/COMMIT_EDITMSG

Regex matches .github/workflows/dco.yml.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

SIGNED_OFF_RE = re.compile(r"^Signed-off-by: .* <.*>$", re.MULTILINE)


def main(argv: list[str]) -> int:
    """Return 0 if the commit message file contains a valid sign-off."""
    if len(argv) != 2:
        print("Usage: check_dco_commit_msg.py <commit-message-file>", file=sys.stderr)
        return 2

    path = Path(argv[1])
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        print(f"ERROR: cannot read commit message file {path}: {exc}", file=sys.stderr)
        return 2

    body = "\n".join(line for line in text.splitlines() if not line.startswith("#"))
    if SIGNED_OFF_RE.search(body):
        return 0

    print("ERROR: Commit message is missing a DCO sign-off.", file=sys.stderr)
    print("Add a line matching: Signed-off-by: Your Name <email@example.com>", file=sys.stderr)
    print("Use: git commit -s", file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
