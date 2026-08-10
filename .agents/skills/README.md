# AAP Containerized Add Node Agent Skills

Agent skills for development workflow and spec-driven development.

## Available Skills

### Spec-Driven Development (SDLC)

| Skill | Purpose | Arguments |
|-------|---------|-----------|
| `sdlc-status` | Show project status and blockers | `[phase or req]` |

## Skill Structure

```
skills/
├── README.md               ← You are here
├── sdlc-status/
│   ├── SKILL.md
│   └── references/
│       └── status-values.md
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
