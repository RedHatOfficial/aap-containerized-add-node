#!/usr/bin/env python3
"""Validate that a PR adds a correct antsibull changelog fragment.

Adapted from ansible/ansible-content-actions
(.github/actions/ansible_validate_changelog/validate_changelog.py).
"""

from __future__ import annotations

import argparse
import logging
import re
import subprocess
import sys
from collections import defaultdict
from pathlib import Path

import yaml

FORMAT = "[%(asctime)s] - %(message)s"
logging.basicConfig(format=FORMAT)
logger = logging.getLogger("validate_changelog")
logger.setLevel(logging.DEBUG)


def is_changelog_file(ref: str) -> bool:
    """Return True if path is a changelog fragment."""
    return bool(re.match(r"^changelogs/fragments/(.*)\.(yaml|yml)$", ref))


def is_module_or_plugin(ref: str) -> bool:
    """Return True if path is collection code that needs a changelog when modified."""
    prefix_list = (
        "plugins/modules",
        "plugins/module_utils",
        "plugins/action",
        "plugins/inventory",
        "plugins/lookup",
        "plugins/filter",
        "plugins/connection",
        "plugins/become",
        "plugins/cache",
        "plugins/callback",
        "plugins/cliconf",
        "plugins/httpapi",
        "plugins/netconf",
        "plugins/shell",
        "plugins/strategy",
        "plugins/terminal",
        "plugins/test",
        "plugins/vars",
        "roles/",
        "playbooks/",
        "meta/runtime.yml",
    )
    return ref.startswith(prefix_list)


def is_release_pr(changes: dict[str, list[str]]) -> bool:
    """Return True if the changeset looks like a collection release."""
    if not set(changes.keys()).issubset(("D", "M")):
        return False
    if not all(is_changelog_file(x) for x in changes.get("D", [])):
        return False
    if not set(changes.get("M", [])).issubset(
        ("CHANGELOG.rst", "changelogs/changelog.yaml", "galaxy.yml")
    ):
        return False
    return True


def is_changelog_needed(changes: dict[str, list[str]]) -> bool:
    """Return True if a new changelog fragment is required for this PR."""
    modifications = changes.get("M", []) + changes.get("D", [])
    return any(is_module_or_plugin(x) for x in modifications)


def is_valid_changelog_format(path: str) -> bool:
    """Return True if the fragment YAML uses allowed section keys."""
    try:
        config = Path("changelogs/config.yaml")
        with open(config, "rb") as config_file:
            changelog_config = yaml.safe_load(config_file)
        changes_type = tuple(item[0] for item in changelog_config["sections"])
        changes_type += (changelog_config["trivial_section_name"],)
        changes_type += (changelog_config["prelude_section_name"],)
        logger.info("Found the following changelog sections: %s", changes_type)
    except (OSError, yaml.YAMLError) as exc:
        logger.info(
            "Failed to read changelog config, using default sections instead: %s",
            exc,
        )
        changes_type = (
            "release_summary",
            "breaking_changes",
            "major_changes",
            "minor_changes",
            "removed_features",
            "deprecated_features",
            "security_fixes",
            "bugfixes",
            "known_issues",
            "trivial",
        )

    try:
        with open(path, "rb") as file_desc:
            result = list(yaml.safe_load_all(file_desc))

        for section in result:
            for key in section.keys():
                if key not in changes_type:
                    logger.error("%s from %s is not a valid changelog type", key, path)
                    return False
                if key == "release_summary" and not isinstance(section[key], str):
                    logger.error("release_summary should not be a list")
                    return False
                if key != "release_summary" and not isinstance(section[key], list):
                    logger.error(
                        "Changelog section %s from file %s must be a list, '%s' found instead.",
                        key,
                        path,
                        type(section[key]),
                    )
                    return False
        return True
    except (OSError, yaml.YAMLError) as exc:
        logger.error("yaml loading error for file %s -> %s", path, exc)
        return False


def run_command(cmd: str) -> tuple[int, str, str]:
    """Run a shell command; return (rc, stdout, stderr)."""
    with subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        shell=True,
        encoding="utf-8",
    ) as proc:
        out, err = proc.communicate()
        return proc.returncode, out, err


def list_files(ref: str) -> dict[str, list[str]]:
    """List files changed vs origin/ref, keyed by git status letter."""
    command = "git diff origin/" + ref + " --name-status"
    logger.info("Executing -> %s", command)
    ret_code, stdout, stderr = run_command(command)
    if ret_code != 0:
        raise ValueError(stderr)

    changes: dict[str, list[str]] = defaultdict(list)
    for file in stdout.split("\n"):
        file_attr = file.split("\t")
        if len(file_attr) == 2:
            changes[file_attr[0]].append(file_attr[1])
    logger.info("changes -> %s", changes)
    return changes


def main(ref: str) -> None:
    """Validate changelog fragments for the PR against base ref."""
    changes = list_files(ref)
    if not changes:
        logger.info("No file changes detected.")
        sys.exit(0)

    if is_release_pr(changes):
        logger.info("This PR looks like a release!")
        sys.exit(0)

    changelog = [x for x in changes.get("A", []) if is_changelog_file(x)]
    logger.info("changelog files -> %s", changelog)
    if not changelog:
        if is_changelog_needed(changes):
            logger.error(
                "Missing changelog fragment. This is not required"
                " only if PR adds new modules and plugins or contain"
                " only documentation changes."
            )
            sys.exit(1)
        logger.info(
            "Changelog not required as PR adds new modules and/or"
            " plugins or contain only documentation changes."
        )
        sys.exit(0)

    invalid_changelog_files = [
        x for x in changelog if not is_valid_changelog_format(x)
    ]
    if invalid_changelog_files:
        logger.error(
            "The following changelog files are not valid -> %s",
            invalid_changelog_files,
        )
        sys.exit(1)
    sys.exit(0)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Validate changelog file from new commit"
    )
    parser.add_argument("--ref", required=True, help="Pull request base ref")
    args = parser.parse_args()
    main(args.ref)
