#!/usr/bin/env python3
"""Extract one version section from CHANGELOG.rst into GitHub-flavored markdown.

Usage:
  python3 .github/scripts/extract_changelog_notes.py --version 1.2.3 --output notes.md
"""

from __future__ import annotations

import argparse
import os
import re
import sys
from pathlib import Path

VERSION_HEADING = re.compile(r"^v(\d+\.\d+\.\d+)\s*$")
CHANGELOG_RST = Path("CHANGELOG.rst")


def extract_section(text: str, version: str) -> list[str]:
    """Return RST lines for vVERSION, excluding the following version heading."""
    lines = text.splitlines()
    start: int | None = None
    for index, line in enumerate(lines):
        match = VERSION_HEADING.match(line)
        if match and match.group(1) == version:
            start = index
            break
    if start is None:
        raise ValueError(f"Version heading v{version} not found in CHANGELOG.rst")

    end = len(lines)
    for index in range(start + 1, len(lines)):
        if VERSION_HEADING.match(lines[index]):
            end = index
            break
    return lines[start:end]


def rst_section_to_markdown(lines: list[str]) -> str:
    """Convert a short antsibull RST section into markdown."""
    rendered: list[str] = []
    index = 0
    while index < len(lines):
        line = lines[index]
        next_line = lines[index + 1] if index + 1 < len(lines) else ""
        if next_line and set(next_line) == {"="} and len(next_line) >= 3:
            rendered.append(f"## {line.strip()}")
            index += 2
            continue
        if next_line and set(next_line) == {"-"} and len(next_line) >= 3:
            rendered.append(f"### {line.strip()}")
            index += 2
            continue
        rendered.append(line.rstrip())
        index += 1

    while rendered and not rendered[-1].strip():
        rendered.pop()
    return "\n".join(rendered).strip() + "\n"


def main() -> int:
    """Write markdown notes for --version to --output."""
    parser = argparse.ArgumentParser(description="Extract changelog notes for a GitHub Release")
    parser.add_argument("--version", required=True, help="Semver MAJOR.MINOR.PATCH (no v prefix)")
    parser.add_argument("--output", required=True, help="Markdown file to write")
    args = parser.parse_args()

    if not CHANGELOG_RST.is_file():
        print("ERROR: CHANGELOG.rst not found", file=sys.stderr)
        return 1

    try:
        section = extract_section(CHANGELOG_RST.read_text(encoding="utf-8"), args.version)
        body = rst_section_to_markdown(section)
    except ValueError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    repo = os.environ.get("GITHUB_REPOSITORY", "RedHatOfficial/aap-containerized-add-node")
    notes = (
        body
        + f"\nSee [CHANGELOG.rst](https://github.com/{repo}/blob/v{args.version}/CHANGELOG.rst) "
        + "for the full history.\n"
    )
    Path(args.output).write_text(notes, encoding="utf-8")
    print(notes)
    return 0


if __name__ == "__main__":
    sys.exit(main())
