# ADR-002: Serial Registration

## Status

Accepted

## Date

2026-08-10

## Context

Adding multiple execution nodes simultaneously causes database race conditions. When parallel `awx-manage provision_instance` commands hit the same controller, one or more fail with constraint violations.

Test case: Run `add_node.yml` with 3 nodes in inventory without serialization — second and third nodes fail intermittently.

## Decision

**Serialize the registration play with `serial: 1`.**

```yaml
- name: Register new instances via awx-manage on controller
  hosts: aap_add_node_targets
  serial: 1  # Serialize registration to avoid DB race condition
  gather_facts: true
  roles:
    - role: register_instance
```

Only registration is serialized. All other plays (host_prep, install_receptor_node) run in parallel.

## Alternatives Considered

### Alternative 1: Retry Loop with Backoff

**Description**: Wrap awx-manage in retry logic with exponential backoff.

**Pros**:
- Faster overall (parallel attempts)

**Cons**:
- Complex retry logic
- Unpredictable timing
- Harder to debug failures

**Why not chosen**: `serial: 1` is simple, deterministic, and fast enough (registration takes ~2 seconds per node).

### Alternative 2: Batch Registration API

**Description**: Call API once with all nodes.

**Pros**:
- Single transaction

**Cons**:
- No such API exists
- Would require upstream contribution

**Why not chosen**: API doesn't exist.

## Consequences

### Positive

- Deterministic success for multi-node runs
- Simple implementation (one line)
- Easy to understand and debug

### Negative

- Multi-node runs take slightly longer (N * ~2s for registration)
- Acceptable tradeoff for reliability

## Implementation

`playbooks/add_node.yml:89`

## References

- Database constraint error observed in testing
- Similar pattern used in `ansible.containerized_installer`

---

## Revision History

| Date | Author | Change |
|------|--------|--------|
| 2026-08-10 | pgriffit | Initial — documenting existing implementation |
