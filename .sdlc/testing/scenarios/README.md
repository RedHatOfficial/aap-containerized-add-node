# Test Scenarios

Lab procedures (`S-*`). The **authoritative status and results log** live in [TEST.md](../../TEST.md) (`T-*` IDs). Keep both aligned using the mapping below.

## Mapping to TEST.md

| Scenario | TEST.md IDs (typical) | Status | Notes |
|----------|------------------------|--------|-------|
| [S-001](S-001-single-en.md) | T-26-AIO-EN, T-27-AIO-EN | :white_check_mark: Tested | EN → controller |
| [S-002](S-002-single-hop.md) | T-26-AIO-HN, T-27-AIO-HN | :white_check_mark: Tested | HN → controller (also covered by EN-VIA-HN) |
| [S-003](S-003-multi-hop.md) | T-26-AIO-EN-VIA-HN, T-27-AIO-EN-VIA-HN | :white_check_mark: Tested | HN + EN via hop, one playbook run |
| S-010 (planned) | — | :white_large_square: Untested | Inbound dial / controller peers to node |
| S-020 | — | :white_check_mark: Tested (with joins) | Covered by [checklists/preflight.md](../checklists/preflight.md) |
| S-030 | Parallel column in TEST.md | :white_check_mark: Tested (implicit in S-003) | Multi-node serial registration |
| [S-040](S-040-failure-recovery.md) | T-26-AIO-RERUN | :white_check_mark: Tested (2.6) | Mid-join failure then re-run |
| [S-041](S-041-deprovision-rejoin.md) | T-26-AIO-DEPROV-REJOIN | :white_check_mark: Tested (2.6) | Deprovision + rejoin |
| [S-050](S-050-upgrade-after-join.md) | T-26-AIO-FULL-UPGRADE | :white_check_mark: Tested (2.6) | Full installer after additive join |
| Cluster (planned) | T-*-CLU-* | :white_large_square: Untested | Multi-controller |

## Scenario index

| ID | Name | Topology | Priority | Status | Detail file |
|----|------|----------|----------|--------|-------------|
| [S-001](S-001-single-en.md) | Single Execution Node | AIO + EN | P1 | :white_check_mark: Tested | Yes |
| [S-002](S-002-single-hop.md) | Single Hop Node | AIO + HN | P1 | :white_check_mark: Tested | Yes |
| [S-003](S-003-multi-hop.md) | Multi-Hop (EN via HN) | AIO + HN + EN | P1 | :white_check_mark: Tested | Yes |
| S-010 | Inbound Dial | AIO + inbound | P2 | :white_large_square: Untested | No — see docs/TOPOLOGY.md |
| S-020 | Preflight Validation | Any | P1 | :white_check_mark: Tested (with joins) | Checklist only |
| S-030 | Parallel / serial multi-node | AIO + 2+ nodes | P1 | :white_check_mark: Tested (via S-003) | Implicit in S-003 |
| [S-040](S-040-failure-recovery.md) | Failure and Recovery | Any | P1 | :white_check_mark: Tested (2.6) | Yes |
| [S-041](S-041-deprovision-rejoin.md) | Deprovision and Rejoin | Any | P1 | :white_check_mark: Tested (2.6) | Yes |
| [S-050](S-050-upgrade-after-join.md) | Full Upgrade After Join | Any | P2 | :white_check_mark: Tested (2.6) | Yes |
| — | Cluster topologies | Multi-controller | P2 | :white_large_square: Untested | No — see T-*-CLU-* |

## Creating or extending a scenario

1. Copy [test-scenario.md](../../templates/test-scenario.md) → `S-NNN-name.md`
2. Link related `T-*` IDs in Metadata / Related
3. Update this index and the mapping table
4. After a lab run: Results Log here **and** [TEST.md](../../TEST.md) Results log

## Running scenarios

1. Lab prereqs: [TEST.md](../../TEST.md) + scenario Prerequisites
2. Local secrets only (`.ignore/lab/` or vault) — never commit credentials
3. Follow Steps; verify with [verification.md](../checklists/verification.md)
4. Record shared results (TEST.md + this file’s Results Log)
5. Optional: keep full ansible stdout under `.ignore/lab/runs/` (gitignored)

## Priority definitions

| Priority | Meaning | When to test |
|----------|---------|--------------|
| P1 | Core functionality | Every release |
| P2 | Important features | Major releases |
| P3 | Edge cases | As needed |
