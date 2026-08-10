# Test Plan

## Scope

| In Scope | Out of Scope |
|----------|--------------|
| Containerized AAP 2.6+ | RPM installs |
| Execution nodes | OpenShift/Operator |
| Hop nodes | AAP 2.4 and earlier |
| RHEL 9/10 nodes | Non-RHEL nodes |
| Outbound dial | — |
| Inbound dial (opt-in) | — |

## Test Matrix

### Platform Compatibility

| AAP Version | Controller OS | Node OS | Priority | Status |
|-------------|---------------|---------|----------|--------|
| 2.6.x | RHEL 9 | RHEL 9 | P1 | Tested |
| 2.7.x | RHEL 10 | RHEL 9 | P1 | Tested (T-27-AIO-EN-VIA-HN, 2026-08-10) |
| 2.7.1 | (lab) | RHEL 10 EN | P1 | Tested (S-001) |
| 2.7.x | RHEL 10 | RHEL 10 HN+EN | P1 | Tested (T-27-AIO-EN-VIA-HN, 2026-08-10) |
| 2.6.x | RHEL 9 | RHEL 10 | P2 | Untested |

### Topology Combinations

| Topology | Node Types | Priority | Status |
|----------|------------|----------|--------|
| AIO + 1 EN | Execution | P1 | Tested |
| AIO + 1 HN | Hop | P1 | Tested |
| AIO + HN + EN via HN | Mixed | P1 | Tested |
| Cluster + EN | Execution | P2 | Untested |
| Cluster + HN | Hop | P2 | Untested |

### Feature Coverage

| Feature | Scenario | Priority | Status |
|---------|----------|----------|--------|
| Outbound dial | S-001, S-002, S-003 | P1 | Tested |
| Inbound dial | S-010 | P2 | Untested |
| Preflight checks | S-020 | P1 | Tested |
| Serial registration | S-030 | P1 | Tested |
| Re-run after failure | S-040 | P1 | Tested |
| Deprovision/rejoin | S-041 | P1 | Tested |
| Full upgrade after join | S-050 | P2 | Tested |

## Test Levels

### Level 1: Static Analysis (CI)

Every commit must pass:

```bash
ansible-lint
ansible-playbook --syntax-check playbooks/*.yml
```

### Level 2: Unit Tests

Role-level validation (future):

```bash
ansible-test units --docker
```

### Level 3: Integration Tests

Multi-role interaction (future):

```bash
ansible-test integration --docker
```

### Level 4: Scenario Tests

End-to-end lab validation:

1. Pick scenario from `scenarios/`
2. Set up lab environment
3. Run scenario steps
4. Record results

## Pass Criteria

### All Scenarios

- [ ] Playbook exit code `0`
- [ ] `awx-manage list_instances` shows new hostname(s)
- [ ] Instances green within 3 minutes
- [ ] Heartbeat recent (< 5 minutes)
- [ ] Correct `node_type` (execution/hop)
- [ ] Execution nodes: `capacity > 0`
- [ ] Topology UI matches `receptor_peers`

### Regression

- [ ] Existing nodes unaffected
- [ ] No service restarts (outbound dial)
- [ ] Re-run is idempotent

## Environment Requirements

| Requirement | Minimum | Recommended |
|-------------|---------|-------------|
| Controller disk | 20 GB | 50 GB |
| Node disk | 32 GB | 64 GB |
| Node RAM | 4 GB | 8 GB |
| SSH access | Passwordless | Passwordless |
| Network | EN → Controller:27199 | — |

## Known Limitations

1. **Cluster topologies untested** — AIO validated (2.6 + 2.7); HA cluster needs validation
2. **No automated scenario runner** — Manual execution required
3. **No molecule / ansible-test integration yet** — CI is lint/build/changelog
4. **Dual IDs** — Lab matrix uses `T-*` in TEST.md; procedures use `S-*` — see [scenarios/README.md](scenarios/README.md#mapping-to-testmd)
