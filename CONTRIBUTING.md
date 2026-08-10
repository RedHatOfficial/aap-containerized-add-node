# Contributing to AAP Containerized Add Node

Thank you for your interest in contributing! This document provides guidelines for contributing to this project.

## IMPORTANT: AI Agent Contributors

**All AI agents working on this repository MUST:**

1. **Read `CLAUDE.md`** — Project constitution and constraints
2. **Read `AGENTS.md`** — Agent roles and architectural invariants
3. **Use skills in `.agents/skills/`** — Follow skill procedures for all SDLC tasks

| Task | Skill |
|------|-------|
| Check status | `/sdlc-status` |
| Create requirement | `/req-new` |
| Capture decision question | `/dr-new` |
| Resolve decision | `/dr-review` |
| Document architecture | `/adr-new` |
| Submit PR | `/pr-new` |

**Do NOT bypass skills** — they contain correct logic and ensure consistency.

## Code of Conduct

This project follows the [Red Hat Community Code of Conduct](https://www.redhat.com/en/about/digital-accessibility). Please be respectful and inclusive in all interactions.

## How to Contribute

### Reporting Issues

1. Check existing issues to avoid duplicates
2. Use issue templates when available
3. Include:
   - AAP version (e.g., 2.7.1)
   - RHEL version on execution nodes
   - Relevant inventory configuration (sanitized)
   - Full error output
   - Steps to reproduce

### Submitting Changes

1. **Fork the repository** and create a branch from `devel`
2. **Branch naming**: `feature/description` or `fix/description`
3. **Make your changes** following the style guidelines below
4. **Test your changes** against a real AAP environment if possible
5. **Submit a pull request** to `devel` branch

### Pull Request Process

1. PRs must target `devel` branch (not `main`)
2. All CI checks must pass
3. At least one maintainer approval required
4. Squash commits before merge (or use squash-merge)

## Development Setup

```bash
# Clone your fork
git clone https://github.com/YOUR_USERNAME/aap-containerized-add-node.git
cd aap-containerized-add-node

# Add upstream remote
git remote add upstream https://github.com/RedHatOfficial/aap-containerized-add-node.git

# Create feature branch
git checkout -b feature/my-feature devel

# Run linting
ansible-lint
yamllint .
```

## Style Guidelines

### Ansible

- Follow [Ansible Best Practices](https://docs.ansible.com/ansible/latest/tips_tricks/ansible_tips_tricks.html)
- Use fully qualified collection names (FQCN)
- Use `ansible.builtin.` prefix for all builtin modules
- Task names must be unique and descriptive
- Use `block/rescue` for error handling where appropriate

### YAML

- 2-space indentation
- No trailing whitespace
- Files end with newline
- Use `true`/`false` (not `yes`/`no`)
- **All YAML files must start with `---`** (document start marker)
- **Line length max 200 chars** — wrap long Jinja expressions with `>-`

### Common Lint Issues

The CI runs `ansible-lint` with production profile. Common issues to avoid:

| Issue | Solution |
|-------|----------|
| `yaml[document-start]` | Add `---` as first line of all YAML files |
| `yaml[line-length]` | Wrap lines >200 chars using YAML folded style (`>-`) |
| `name[template]` | Allowed — we use Jinja in task names for per-host context |
| `var-naming[no-role-prefix]` | Allowed — collection uses shared `aap_add_node_*` prefix |
| `no-handler` | Allowed — some `when: changed` tasks aren't handlers |

**Example wrapping long lines:**
```yaml
# Bad - 296 characters
aap_add_node_receptor_image: "{{ 'registry.redhat.io/' ~ (hostvars['aap_add_node_operator'].aap_add_node_default_registry_ns_aap | default('ansible-automation-platform-26')) ~ '/' ~ (hostvars['aap_add_node_operator'].aap_add_node_default_receptor_image | default('receptor-rhel9:latest')) }}"

# Good - wrapped with >-
aap_add_node_receptor_image: >-
  {{ 'registry.redhat.io/' ~
     (hostvars['aap_add_node_operator'].aap_add_node_default_registry_ns_aap | default('ansible-automation-platform-26')) ~ '/' ~
     (hostvars['aap_add_node_operator'].aap_add_node_default_receptor_image | default('receptor-rhel9:latest')) }}
```

### Documentation

- Update README.md for user-facing changes
- Every role under `roles/<name>/` must have a `README.md`
- New roles must include `meta/argument_specs.yml` (no Jinja in argspec
  defaults/descriptions)
- Add an antsibull changelog fragment under `changelogs/fragments/` for changes that
  modify `roles/`, `playbooks/`, or plugins (CI enforces this on PRs)
- Use present tense ("Add feature" not "Added feature")
- Apply the `skip-changelog` label only for docs-only or infra PRs that do not need a fragment

#### Changelog fragments

Release notes are generated into [CHANGELOG.rst](CHANGELOG.rst) via antsibull-changelog.
[CHANGELOG.md](CHANGELOG.md) only points at that file — do not maintain duplicate release notes there.

Example fragment (`changelogs/fragments/my-change.yml`):

```yaml
---
bugfixes:
  - Fix receptor peer list parsing for INI inventories.
```

Valid section keys are defined in `changelogs/config.yaml` (e.g. `minor_changes`,
`bugfixes`, `breaking_changes`, `trivial`).

## Security

- **Never commit credentials** - use vault references
- **Never hardcode paths** - use variables
- **Validate user input** - especially `receptor_peers` format
- Report security issues per SECURITY.md

## Testing

### Local Testing

```bash
# Lint
ansible-lint
yamllint .

# Syntax check
ansible-playbook playbooks/add_node.yml --syntax-check
```

### Integration Testing

Test against a real AAP environment:
1. Containerized AAP 2.6+ with running controller
2. RHEL 9 or 10 execution node (minimal install)
3. SSH key authentication configured

## Release Process

1. Changes merge to `devel`
2. When ready for release, `devel` merges to `main`
3. Run `antsibull-changelog release` (updates `CHANGELOG.rst` / `changelogs/changelog.yaml`) and bump `galaxy.yml` version
4. Tag created on `main` (e.g., `v1.0.0`)
5. `release.yml` builds the collection and attaches the `.tar.gz` to a GitHub Release
6. Distribute that tarball to customers manually (not published to Ansible Galaxy or Automation Hub)

## Questions?

- Open a GitHub Discussion
- Contact maintainers via issue comments
