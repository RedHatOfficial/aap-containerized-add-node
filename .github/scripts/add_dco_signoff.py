#!/usr/bin/env python3
"""Add a Signed-off-by trailer if it is missing (same as git commit -s).

Used as a prepare-commit-msg hook. Git does not skip that hook for --no-verify,
so Cursor / `git commit --no-verify` still get a sign-off.

Identity, in order:
  1. git config dco.signoff  (e.g. "Name <email>" for this repo)
  2. git committer ident (GIT_COMMITTER_IDENT), same as git commit -s
"""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

COMMITTER_RE = re.compile(r"^(.*<[^>]+>)")


def git_output(args: list[str]) -> str:
    """Return git stdout, or empty string if the command fails."""
    proc = subprocess.run(
        ["git", *args],
        check=False,
        capture_output=True,
        text=True,
    )
    return proc.stdout.strip() if proc.returncode == 0 else ""


def signoff_line() -> str:
    """Return a full Signed-off-by: Name <email> line."""
    configured = git_output(["config", "--get", "dco.signoff"])
    if configured:
        if configured.lower().startswith("signed-off-by:"):
            return configured
        return f"Signed-off-by: {configured}"

    ident = git_output(["var", "GIT_COMMITTER_IDENT"])
    match = COMMITTER_RE.match(ident)
    if not match:
        raise RuntimeError("Could not determine committer identity for Signed-off-by")
    return f"Signed-off-by: {match.group(1)}"


def main(argv: list[str]) -> int:
    """Insert Signed-off-by into the commit message file if missing."""
    if len(argv) < 2:
        print("Usage: add_dco_signoff.py <commit-message-file>", file=sys.stderr)
        return 2

    msg_file = Path(argv[1])
    try:
        trailer = signoff_line()
    except RuntimeError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    proc = subprocess.run(
        [
            "git",
            "interpret-trailers",
            "--in-place",
            "--if-exists",
            "addIfDifferent",
            "--if-missing",
            "add",
            "--trailer",
            trailer,
            str(msg_file),
        ],
        check=False,
        capture_output=True,
        text=True,
    )
    if proc.returncode != 0:
        print(proc.stderr or proc.stdout, file=sys.stderr)
        return proc.returncode
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
