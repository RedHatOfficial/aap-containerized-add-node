#!/usr/bin/env python3
"""Calculate the next collection version from git tags and changelog fragments.

Usage:
  python3 .github/scripts/calculate_release_version.py
  python3 .github/scripts/calculate_release_version.py --version 1.2.3

If --version / REQUESTED_VERSION is omitted, bump the latest vMAJOR.MINOR.PATCH
tag (falling back to GitHub releases, then galaxy.yml) based on fragment
section keys:

  major_changes / breaking_changes -> major
  minor_changes                    -> minor
  any other fragment               -> patch

Writes GitHub Actions outputs when GITHUB_OUTPUT is set, and a job summary
when GITHUB_STEP_SUMMARY is set.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    yaml = None  # type: ignore[assignment]

SEMVER_RE = re.compile(r"^v?(\d+)\.(\d+)\.(\d+)$")
GALAXY_VERSION_RE = re.compile(
    r"^version:\s*['\"]?(\d+\.\d+\.\d+)(?:-devel)?['\"]?\s*$",
    re.MULTILINE,
)
MAJOR_SECTIONS = {"major_changes", "breaking_changes"}
MINOR_SECTIONS = {"minor_changes"}
FRAGMENTS_DIR = Path("changelogs/fragments")
GALAXY_YML = Path("galaxy.yml")


def run_cmd(args: list[str]) -> tuple[int, str, str]:
    """Run a command; return (rc, stdout, stderr)."""
    proc = subprocess.run(
        args,
        check=False,
        capture_output=True,
        text=True,
    )
    return proc.returncode, proc.stdout.strip(), proc.stderr.strip()


def parse_semver(value: str) -> tuple[int, int, int] | None:
    """Return (major, minor, patch) or None if value is not X.Y.Z / vX.Y.Z."""
    match = SEMVER_RE.match(value.strip())
    if not match:
        return None
    return int(match.group(1)), int(match.group(2)), int(match.group(3))


def format_version(parts: tuple[int, int, int]) -> str:
    """Format (major, minor, patch) as X.Y.Z."""
    return f"{parts[0]}.{parts[1]}.{parts[2]}"


def bump_version(current: tuple[int, int, int], level: str) -> tuple[int, int, int]:
    """Bump current version by major, minor, or patch."""
    major, minor, patch = current
    if level == "major":
        return major + 1, 0, 0
    if level == "minor":
        return major, minor + 1, 0
    return major, minor, patch + 1


def normalize_requested(value: str) -> str:
    """Strip whitespace and an optional v prefix; validate X.Y.Z."""
    cleaned = value.strip()
    if cleaned.lower().startswith("v"):
        cleaned = cleaned[1:]
    if parse_semver(cleaned) is None:
        raise ValueError(
            f"collection_version must be semver MAJOR.MINOR.PATCH (digits only), got: {value!r}"
        )
    return cleaned


def git_semver_tags() -> list[tuple[int, int, int]]:
    """Return parsed semver tags in the local repo."""
    rc, stdout, _stderr = run_cmd(["git", "tag", "--list"])
    if rc != 0 or not stdout:
        return []
    versions: list[tuple[int, int, int]] = []
    for line in stdout.splitlines():
        parsed = parse_semver(line.strip())
        if parsed:
            versions.append(parsed)
    return versions


def github_semver_releases() -> list[tuple[int, int, int]]:
    """Return parsed semver tags from GitHub Releases when gh is available."""
    if not shutil.which("gh"):
        return []
    rc, stdout, _stderr = run_cmd(
        ["gh", "release", "list", "--limit", "50", "--json", "tagName"]
    )
    if rc != 0 or not stdout:
        return []
    try:
        releases = json.loads(stdout)
    except json.JSONDecodeError:
        return []
    versions: list[tuple[int, int, int]] = []
    for item in releases:
        parsed = parse_semver(str(item.get("tagName", "")))
        if parsed:
            versions.append(parsed)
    return versions


def set_galaxy_version(version: str) -> None:
    """Rewrite the version: field in galaxy.yml."""
    normalized = normalize_requested(version)
    if not GALAXY_YML.is_file():
        raise FileNotFoundError("galaxy.yml not found")
    text = GALAXY_YML.read_text(encoding="utf-8")
    updated, count = re.subn(
        r"^version:.*$",
        f"version: {normalized}",
        text,
        count=1,
        flags=re.MULTILINE,
    )
    if count != 1:
        raise RuntimeError("Failed to update version: in galaxy.yml")
    GALAXY_YML.write_text(updated, encoding="utf-8")
    notice(f"Set galaxy.yml version to {normalized}")


def galaxy_version() -> tuple[int, int, int] | None:
    """Return version from galaxy.yml, ignoring an optional -devel suffix."""
    if not GALAXY_YML.is_file():
        return None
    text = GALAXY_YML.read_text(encoding="utf-8")
    match = GALAXY_VERSION_RE.search(text)
    if not match:
        return None
    return parse_semver(match.group(1))


def current_version() -> tuple[tuple[int, int, int], str]:
    """Resolve the highest known released version and where it came from."""
    candidates: list[tuple[tuple[int, int, int], str]] = []
    for parsed in git_semver_tags():
        candidates.append((parsed, "git-tag"))
    for parsed in github_semver_releases():
        candidates.append((parsed, "github-release"))
    galaxy = galaxy_version()
    if galaxy:
        candidates.append((galaxy, "galaxy.yml"))
    if not candidates:
        raise RuntimeError(
            "No semver git tag, GitHub release, or galaxy.yml version found. "
            "Pass --version MAJOR.MINOR.PATCH (or the workflow collection_version input)."
        )
    best, source = max(candidates, key=lambda item: item[0])
    return best, source


def fragment_paths() -> list[Path]:
    """Return changelog fragment files (yml/yaml only)."""
    if not FRAGMENTS_DIR.is_dir():
        return []
    paths = list(FRAGMENTS_DIR.glob("*.yml")) + list(FRAGMENTS_DIR.glob("*.yaml"))
    return sorted(path for path in paths if path.name != ".plugin-cache.yaml")


def fragment_section_keys(path: Path) -> set[str]:
    """Return section keys from a fragment file."""
    if yaml is None:
        raise RuntimeError("PyYAML is required to read changelog fragments (pip install pyyaml)")
    with path.open("rb") as handle:
        documents = list(yaml.safe_load_all(handle))
    keys: set[str] = set()
    for document in documents:
        if isinstance(document, dict):
            keys.update(str(key) for key in document)
    return keys


def change_level_from_fragments(paths: list[Path]) -> str:
    """Return major, minor, or patch from fragment section keys."""
    keys: set[str] = set()
    for path in paths:
        keys.update(fragment_section_keys(path))
    if keys & MAJOR_SECTIONS:
        return "major"
    if keys & MINOR_SECTIONS:
        return "minor"
    return "patch"


def write_output(name: str, value: str) -> None:
    """Append name=value to GITHUB_OUTPUT when set."""
    output_path = os.environ.get("GITHUB_OUTPUT")
    if not output_path:
        return
    with open(output_path, "a", encoding="utf-8") as handle:
        handle.write(f"{name}={value}\n")


def write_summary(rows: list[tuple[str, str]]) -> None:
    """Write a markdown table to GITHUB_STEP_SUMMARY when set."""
    summary_path = os.environ.get("GITHUB_STEP_SUMMARY")
    if not summary_path:
        return
    lines = [
        "## Release version preview",
        "",
        "| Field | Value |",
        "| --- | --- |",
    ]
    lines.extend(f"| {key} | `{value}` |" for key, value in rows)
    lines.extend(
        [
            "",
            "Schedule runs (1st and 15th) always auto-calculate the version.",
            "Manual runs use the collection_version input when set, otherwise auto-calculate.",
            "",
        ]
    )
    with open(summary_path, "a", encoding="utf-8") as handle:
        handle.write("\n".join(lines))


def notice(message: str) -> None:
    """Print a GitHub Actions notice (or a plain line locally)."""
    print(f"::notice::{message}" if os.environ.get("GITHUB_ACTIONS") else message)


def warn(message: str) -> None:
    """Print a GitHub Actions warning (or a plain line locally)."""
    print(f"::warning::{message}" if os.environ.get("GITHUB_ACTIONS") else f"WARNING: {message}")


def error(message: str) -> None:
    """Print a GitHub Actions error (or a plain line locally)."""
    print(f"::error::{message}" if os.environ.get("GITHUB_ACTIONS") else f"ERROR: {message}")


def main() -> int:
    """Calculate version and emit outputs."""
    parser = argparse.ArgumentParser(description="Calculate next collection release version")
    parser.add_argument(
        "--version",
        default="",
        help="Optional semver MAJOR.MINOR.PATCH. Overrides auto-calculation from fragments.",
    )
    parser.add_argument(
        "--set-galaxy",
        metavar="VERSION",
        default="",
        help="Rewrite galaxy.yml version to VERSION and exit.",
    )
    args = parser.parse_args()

    if args.set_galaxy:
        try:
            set_galaxy_version(args.set_galaxy)
        except (ValueError, OSError, RuntimeError) as exc:
            error(str(exc))
            return 1
        return 0

    requested_raw = (args.version or os.environ.get("REQUESTED_VERSION", "")).strip()
    fragments = fragment_paths()
    has_fragments = bool(fragments)
    level = change_level_from_fragments(fragments) if fragments else "patch"

    current, current_source = current_version()
    current_str = format_version(current)

    if requested_raw:
        try:
            collection_version = normalize_requested(requested_raw)
        except ValueError as exc:
            error(str(exc))
            return 1
        version_source = "input"
        change_present = "true"
        parsed_requested = parse_semver(collection_version)
        assert parsed_requested is not None
        if parsed_requested <= current:
            warn(
                f"Requested version {collection_version} is not greater than "
                f"current {current_str} (from {current_source})."
            )
    else:
        version_source = "auto"
        collection_version = format_version(bump_version(current, level))
        change_present = "true" if has_fragments else "false"
        if change_present == "false":
            notice(
                f"No changelog fragments found. Reporting would-be {level} bump "
                f"{current_str} -> {collection_version}; release will be skipped."
            )

    tag_name = f"v{collection_version}"
    existing_tags = {format_version(item) for item in git_semver_tags()}
    if collection_version in existing_tags:
        message = f"Git tag v{collection_version} (or {collection_version}) already exists."
        if change_present == "true":
            error(message)
            return 1
        warn(message)

    rows = [
        ("collection_version", collection_version),
        ("tag_name", tag_name),
        ("change_level", level),
        ("change_present", change_present),
        ("version_source", version_source),
        ("current_version", current_str),
        ("current_source", current_source),
        ("fragment_count", str(len(fragments))),
    ]
    for key, value in rows:
        write_output(key, value)
        print(f"{key}={value}")

    write_summary(rows)
    notice(
        f"Calculated version {collection_version} (tag {tag_name}, "
        f"{level}, source={version_source}, fragments={len(fragments)})"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
