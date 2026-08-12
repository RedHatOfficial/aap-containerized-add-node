# Test Plan

Test results: [results/RESULTS.md](results/RESULTS.md)

## Scope

| In Scope | Out of Scope |
|----------|--------------|
| Containerized AAP 2.6+ | RPM installs |
| Execution nodes | OpenShift/Operator |
| Hop nodes | AAP 2.4 and earlier |
| RHEL 9/10 nodes | Non-RHEL nodes |
| Outbound dial | — |
| Inbound dial (opt-in) | — |

## Lab Infrastructure

### Hosts

| Host | OS | Role | Notes |
|------|-----|------|-------|
| carmaap1.lan | RHEL 9 | Controller (AIO) | AAP 2.6 containerized |
| aap-exec1-rhel9 | RHEL 9 | EN | Permanent |
| aap-exec1-rhel10 | RHEL 10 | EN | Permanent |
| aap-flex1-rhel9 | RHEL 9 | HN or EN | Flexible — deprovision/reprovision between tests |
| aap-flex1-rhel10 | RHEL 10 | HN or EN | Flexible — deprovision/reprovision between tests |

### Test Strategy

- Same-OS pairing: HN and EN share RHEL version (matches customer scenarios)
- Flex hosts: deprovision and reprovision as HN or EN per test
- E2E validation: Demo Template must run on EN (HN alone = no job execution)

## Test Matrix

### Platform Compatibility

| AAP Version | Controller OS | Node OS | Priority | Status |
|-------------|---------------|---------|----------|--------|
| 2.6.x | RHEL 9 | RHEL 9 | P1 | Tested |
| 2.7.x | RHEL 10 | RHEL 9 | P1 | Tested (T-27-AIO-EN-VIA-HN, 2026-08-10) |
| 2.7.1 | (lab) | RHEL 10 EN | P1 | Tested (S-001) |
| 2.7.x | RHEL 10 | RHEL 10 HN+EN | P1 | Tested (T-27-AIO-EN-VIA-HN, 2026-08-10) |
| 2.7.x | RHEL 10 HA | RHEL 10 HN+EN | P1 | Tested (T-27-CLU-EN-VIA-HN, 2026-08-12) |
| 2.6.x | RHEL 9 | RHEL 10 | P2 | Tested (2026-08-11) |

### Topology Combinations

| Topology | flex-rhel9 | flex-rhel10 | exec-rhel9 | exec-rhel10 | Priority | Status |
|----------|------------|-------------|------------|-------------|----------|--------|
| Single EN (RHEL 9) | — | — | EN | — | P1 | Tested |
| Single EN (RHEL 10) | — | — | — | EN | P1 | Tested |
| Parallel 2 ENs | — | — | EN | EN | P1 | Tested |
| Parallel 4 ENs | EN | EN | EN | EN | P2 | Untested |
| RHEL 9 HN + EN | HN | — | EN behind | — | P1 | Tested (2026-08-11) |
| RHEL 10 HN + EN | — | HN | — | EN behind | P1 | Tested (2026-08-11) |
| Chain HN→HN→EN | HN | HN | EN behind | — | P2 | Untested |
| Cluster + EN | — | — | EN | — | P2 | Untested |
| Cluster + HN + EN | HN | — | EN behind | — | P2 | Tested (T-27-CLU-EN-VIA-HN, 2026-08-12) |

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

1. **2.6 cluster untested** — 2.7 HA cluster validated (RHEL 10, 2026-08-12); 2.6 multi-controller still open
2. **No automated scenario runner** — Manual execution required
3. **No molecule / ansible-test integration yet** — CI is lint/build/changelog
4. **Dual IDs** — Lab matrix uses `T-*` in TEST.md; procedures use `S-*` — see [scenarios/README.md](scenarios/README.md#mapping-to-testmd)
5. **Flex hosts required** — aap-flex1-rhel9 and aap-flex1-rhel10 must be provisioned for HN testing
