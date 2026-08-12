# Test Results

Consolidated test results for `redhat_official.aap_containerized_add_node`.

See [TEST.md](../../../TEST.md) for scenario definitions and [test-plan.md](../test-plan.md) for the test matrix.

## Results Log

| Date | Scenario | AAP | Controller OS | Node OS | Topology | Result | Notes |
|------|----------|-----|---------------|---------|----------|--------|-------|
| 2026-08 | T-26-AIO-EN | 2.6 | RHEL 9 | RHEL 9 | EN→Controller | Pass | Single EN |
| 2026-08 | T-26-AIO-HN | 2.6 | RHEL 9 | RHEL 9 | HN→Controller | Pass | Single HN |
| 2026-08 | T-26-AIO-EN-VIA-HN | 2.6 | RHEL 9 | RHEL 9 | EN→HN→Controller | Pass | Combined mesh |
| 2026-08-07 | T-26-AIO-RERUN | 2.6 | RHEL 9 | RHEL 9 | EN→HN→Controller | Pass | After 64G resize |
| 2026-08-07 | T-26-AIO-DEPROV-REJOIN | 2.6 | RHEL 9 | RHEL 9 | EN→HN→Controller | Pass | New VMs, same names |
| 2026-08-07 | T-26-AIO-FULL-UPGRADE | 2.6 | RHEL 9 | RHEL 9 | Existing mesh | Pass | Full installer upgrade |
| 2026-08 | T-27-AIO-EN | 2.7.1 | RHEL 10 | RHEL 9/10 | EN→Controller | Pass | Both OS tested |
| 2026-08-10 | T-27-AIO-EN-VIA-HN | 2.7 | RHEL 10 | RHEL 9 | EN→HN→Controller | Pass | RHEL 9 HN+EN |
| 2026-08-10 | T-27-AIO-EN-VIA-HN | 2.7 | RHEL 10 | RHEL 10 | EN→HN→Controller | Pass | RHEL 10 HN+EN |
| 2026-08-11 | T-26-AIO-EN-VIA-HN | 2.6 | RHEL 9 | RHEL 9 | EN→HN→Controller | Pass | carmaap1 lab |
| 2026-08-11 | T-26-AIO-EN-VIA-HN | 2.6 | RHEL 9 | RHEL 10 | EN→HN→Controller | Pass | carmaap1 lab |
| 2026-08-12 | T-27-CLU-EN-VIA-HN | 2.7 | RHEL 10 | RHEL 10 | EN→HN→Controller (HA) | Pass | 11-node cluster; gateway control host |
| 2026-08-12 | T-27-CLU-HN | 2.7 | RHEL 10 | RHEL 10 | HN→Controller (HA) | Pass | Same run as CLU EN-VIA-HN |

## Coverage Summary

| Topology | RHEL 9 | RHEL 10 |
|----------|--------|---------|
| Single EN → Controller | ✅ | ✅ |
| Single HN → Controller | ✅ | ✅ |
| EN → HN → Controller | ✅ | ✅ |
| Parallel ENs | ✅ | Untested |
| HA Cluster + EN via HN | Untested | ✅ |
| HA Cluster + HN only | Untested | ✅ (via EN-VIA-HN join) |

## Lab Environments

| Lab | Controller | AAP Version | Notes |
|-----|------------|-------------|-------|
| carmaap1.lan | RHEL 9 AIO | 2.6 | Primary test lab |
| aap27 (lennysh) | RHEL 10 AIO | 2.7 | Secondary lab |
| aap27 cluster (lennysh) | RHEL 10 HA (2× controller) | 2.7 | 11-node; gateway control host |

## Node Inventory

Tested nodes on carmaap1 lab:

| Host | OS | Roles Tested |
|------|-----|--------------|
| aap-exec1-rhel9 | RHEL 9 | EN |
| aap-flex1-rhel9 | RHEL 9 | HN |
| aap-exec1-rhel10 | RHEL 10 | EN |
| aap-flex1-rhel10 | RHEL 10 | HN |
