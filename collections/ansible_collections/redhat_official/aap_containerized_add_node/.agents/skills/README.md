# AAP Containerized Add Node Agent Skills

Agent skills for development workflow and spec-driven development.

## Available Skills

### Spec-Driven Development (SDLC)

| Skill | Purpose | Arguments |
|-------|---------|-----------|
| `sdlc-status` | Show project status and blockers | `[phase or req]` |
| `workflow` | Get workflow guidance | `[next\|blockers\|start\|decision]` |
| `req-new` | Create requirement spec | `[Feature] [--phase X]` |
| `dr-new` | Create Decision Request | `[Question] [--priority X]` |
| `dr-review` | Resolve Decision Request | `[DR-NNN] [--quick]` |
| `adr-new` | Create Architecture Decision Record | `[Title] [--from-dr X]` |

### Pull Requests

| Skill | Purpose | Arguments |
|-------|---------|-----------|
| `pr-new` | Prepare and submit a pull request | `[branch-name] [--title 'PR title']` |

### Utilities

| Skill | Purpose | Arguments |
|-------|---------|-----------|
| `lean-ci` | Guide for GitHub Actions workflows | `[workflow-name]` |

## Skill Structure

```
skills/
├── README.md               ← You are here
├── sdlc-status/
│   ├── SKILL.md
│   └── references/
│       └── status-values.md
├── workflow/
│   └── SKILL.md
├── req-new/
│   └── SKILL.md
├── dr-new/
│   └── SKILL.md
├── dr-review/
│   └── SKILL.md
├── adr-new/
│   └── SKILL.md
├── pr-new/
│   └── SKILL.md
└── lean-ci/
    └── SKILL.md
```

## SKILL.md Format

Each skill has YAML frontmatter:

```yaml
---
name: skill-name
description: >-
  What the skill does. When to use it. Trigger phrases.
  When NOT to use it.
argument-hint: "[expected arguments]"
user-invocable: true
metadata:
  author: AAP Add Node Team
  version: 1.0.0
---
```

## Agent Invocation Policy

SDLC skills may be invoked by the agent proactively during development
when the context warrants it (e.g., creating an ADR after an architectural
decision is made). The agent informs the user when it creates an artifact.

## Version

- **Version**: 1.0.0
- **Author**: AAP Add Node Team
- **License**: Apache 2.0
