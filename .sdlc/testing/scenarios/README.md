# Test Scenarios

Lab procedures (`S-*`). The **authoritative status and results log** live in [TEST.md](../../TEST.md) (`T-*` IDs). Keep both aligned using the mapping below.

## Mapping to TEST.md

| Scenario | TEST.md IDs (typical) | Status | Notes |
|----------|------------------------|--------|-------|
| [S-001](S-001-single-en.md) | T-26-AIO-EN, T-27-AIO-EN | :white_check_mark: Tested | EN → controller |
| [S-002](S-002-single-hop.md) | T-26-AIO-HN, T-27-AIO-HN, T-27-CLU-HN | :white_check_mark: Tested | HN → controller (AIO + HA cluster; RHEL 9 + 10) |
| [S-003](S-003-multi-hop.md) | T-26-AIO-EN-VIA-HN, T-27-AIO-EN-VIA-HN, T-27-CLU-EN-VIA-HN | :white_check_mark: Tested | HN + EN via hop; AIO + 2.7 HA cluster (RHEL 10) |
| S-010 (planned) | — | :white_large_square: Untested | Inbound dial / controller peers to node |
| S-020 | — | :white_check_mark: Tested (with joins) | Covered by [checklists/preflight.md](../checklists/preflight.md) |
| S-030 | Parallel column in TEST.md | :white_check_mark: Tested (implicit in S-003) | Multi-node serial registration |
| [S-040](S-040-failure-recovery.md) | T-26-AIO-RERUN | :white_check_mark: Tested (2.6) | Mid-join failure then re-run |
| [S-041](S-041-deprovision-rejoin.md) | T-26-AIO-DEPROV-REJOIN | :white_check_mark: Tested (2.6) | Deprovision + rejoin |
| [S-050](S-050-upgrade-after-join.md) | T-26-AIO-FULL-UPGRADE | :white_check_mark: Tested (2.6) | Full installer after additive join |
| [S-060](S-060-offline-bundle-en.md) | — | :white_large_square: Untested | Offline bundle - single EN |
| [S-061](S-061-offline-bundle-hn.md) | — | :white_large_square: Untested | Offline bundle - single HN |
| [S-062](S-062-offline-bundle-with-images.md) | — | :white_large_square: Untested | Offline bundle with container images |
| [S-063](S-063-offline-bundle-hn-en-chain.md) | — | :white_large_square: Untested | Offline bundle - HN + EN chain |
| [S-064](S-064-offline-hybrid-cloud.md) | — | :white_large_square: Untested | Offline hybrid cloud simulation |
| Cluster (planned) | T-27-CLU-EN-VIA-HN, T-27-CLU-HN | :white_check_mark: Tested (2.7) | Multi-controller; RHEL 10 lab 2026-08-12 |

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
| [S-060](S-060-offline-bundle-en.md) | Offline Bundle - EN | AIO + EN offline | P1 | :white_large_square: Untested | Yes |
| [S-061](S-061-offline-bundle-hn.md) | Offline Bundle - HN | AIO + HN offline | P1 | :white_large_square: Untested | Yes |
| [S-062](S-062-offline-bundle-with-images.md) | Offline Bundle + Images | AIO + EN airgap | P2 | :white_large_square: Untested | Yes |
| [S-063](S-063-offline-bundle-hn-en-chain.md) | Offline Bundle - HN+EN Chain | AIO + HN + EN offline | P1 | :white_large_square: Untested | Yes |
| [S-064](S-064-offline-hybrid-cloud.md) | Offline Hybrid Cloud | Cloud + on-prem offline | P2 | :white_large_square: Untested | Yes |
| — | Cluster topologies | Multi-controller | P2 | :white_check_mark: Tested (2.7 RHEL 10) | EN-VIA-HN — see T-27-CLU-* |

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
