# ADR-005: Preflight as Opt-Out

## Status

Accepted

## Date

2026-08-10

## Context

Common failure modes when adding nodes:
- SSH keys not configured
- Registry credentials missing/expired
- Controller container not running
- Network connectivity blocked
- DNS resolution failures

These surface mid-install, wasting time and leaving partial state.

## Decision

**Preflight checks enabled by default. Skip with explicit flag.**

```yaml
- name: Preflight checks
  hosts: localhost
  roles:
    - role: preflight
      when: aap_add_node_preflight_enabled | default(true) | bool
```

Skip: `-e aap_add_node_preflight_enabled=false`

Checks run before any changes to target systems.

## Alternatives Considered

### Alternative 1: Opt-In Preflight

**Description**: Preflight disabled by default, enable with flag.

**Pros**:
- Faster for experienced users

**Cons**:
- New users hit mid-install failures
- Most users forget to run preflight

**Why not chosen**: Safety by default. Experienced users can skip.

### Alternative 2: Integrated Checks (No Separate Phase)

**Description**: Each role validates its own preconditions.

**Pros**:
- No separate play

**Cons**:
- Failures happen mid-install
- Partial state left behind
- Harder to run standalone

**Why not chosen**: Separate preflight catches all issues before any changes.

## Consequences

### Positive

- Fail fast before touching targets
- Clear error messages with fix suggestions
- Standalone `preflight.yml` for CI/pipelines
- No partial state on failure

### Negative

- Adds ~10 seconds to run time
- Some checks may be overly cautious

### Neutral

- Skip flag available for repeat runs

## Implementation

- `roles/preflight/` — all checks
- `playbooks/preflight.yml` — standalone execution
- `playbooks/add_node.yml:20-26` — integrated into main playbook

## Checks Performed

| Check | Catches |
|-------|---------|
| SSH connectivity | Key/access issues |
| Controller container | Container not running |
| Registry credentials | Missing/expired auth |
| Network EN→Controller | Firewall blocks |
| DNS resolution | Name resolution failures |
| `receptor_peers` format | Config errors |

## References

- AAPRFE-1752: 7 manual steps problem (preflight reduces)
- `docs/TROUBLESHOOTING.md`: Common issues

---

## Revision History

| Date | Author | Change |
|------|--------|--------|
| 2026-08-10 | pgriffit | Initial — documenting existing implementation |
