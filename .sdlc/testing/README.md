# Testing Framework

Structured testing approach for validating the collection.

## Test Types

| Type | Location | Purpose | When to Run |
|------|----------|---------|-------------|
| Static Analysis | CI | Lint, syntax, YAML validation | Every commit |
| Unit Tests | `tests/unit/` | Role logic validation | Every commit |
| Integration Tests | `tests/integration/` | Role interaction | Pre-release |
| Scenario Tests | `scenarios/` | End-to-end lab validation | Pre-release |

## Directory Structure

```
.sdlc/testing/
├── README.md              ← You are here
├── test-plan.md           # Overall test strategy
├── scenarios/             # Lab test scenarios
│   ├── README.md
│   ├── S-001-single-en.md
│   ├── S-002-single-hop.md
│   ├── S-003-multi-hop.md
│   └── ...
├── checklists/            # Pre-flight and verification
│   ├── preflight.md
│   └── verification.md
└── results/               # Test run results (gitignored)
    └── .gitkeep

tests/                     # Ansible test structure
├── unit/                  # ansible-test unit tests
└── integration/           # ansible-test integration tests
```

## Quick Reference

| Task | Command |
|------|---------|
| Lint | `ansible-lint` |
| Syntax check | `ansible-playbook --syntax-check playbooks/*.yml` |
| Run scenario | See scenario file for specific commands |
| Record result | Update scenario's "Results Log" section |

## Test Artifacts

- **TEST.md** (root): Quick reference and results log
- **scenarios/**: Detailed test procedures
- **checklists/**: Reusable verification steps
