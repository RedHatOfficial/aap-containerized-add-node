---
name: Bug Report
about: Report a problem with the collection
title: '[BUG] '
labels: bug, triage
assignees: ''
---

## Environment

- **AAP Version**: (e.g., 2.7.1)
- **Controller OS**: (e.g., RHEL 9.4)
- **Execution Node OS**: (e.g., RHEL 10.0)
- **Collection Version**: (e.g., 1.0.0)
- **ansible-core Version**: (e.g., 2.16.3)

## Description

A clear description of the bug.

## Steps to Reproduce

1. Configure inventory with...
2. Run `ansible-playbook...`
3. See error

## Expected Behavior

What you expected to happen.

## Actual Behavior

What actually happened.

## Inventory (sanitized)

```ini
[automationcontroller]
controller.example.com

[execution_nodes]
exec1.example.com receptor_peers='["controller.example.com"]'
```

## Error Output

```
Paste relevant error output here
```

## Additional Context

Any other context about the problem.
