# S-040: Failure and Recovery (re-run mid-join)

## Metadata

- **Priority**: P1
- **Topology**: Any (lab: AIO + EN/HN)
- **Status**: Tested (2.6)
- **TEST.md**: T-26-AIO-RERUN

## Description

Confirm incomplete nodes (registered or partially prepared, **no** healthy heartbeat) are targeted again on re-run **without** `deprovision_instance`.

## Prerequisites

| Requirement | Value |
|-------------|-------|
| Controller | Containerized AAP 2.6+ with a failed or interrupted prior join |
| Inventory | Same hosts still under `[execution_nodes]` |
| Fix | Underlying failure resolved (disk, podman, SSH, etc.) |

## Steps

1. Start a normal join; interrupt or fail mid-play (lab: image load `ENOSPC` on small root).
2. Fix the issue (e.g. resize root to ≥32–64 GB).
3. Re-run the **same** `playbooks/add_node.yml` / inventory **without** `deprovision_instance`.
4. Verify with [verification.md](../checklists/verification.md).

## Pass Criteria

- [ ] Playbook exit `0`
- [ ] Hosts reach green; `provision_instance` / receptor install behave idempotently
- [ ] No manual DB cleanup required

## Failure Recovery

If re-run still fails after fix: see [TROUBLESHOOTING.md](../../../docs/TROUBLESHOOTING.md). Last resort: `awx-manage deprovision_instance` then S-041.

## Related

- [S-041](S-041-deprovision-rejoin.md), [S-003](S-003-multi-hop.md)
- TEST.md Known lab pitfalls (disk / ENOSPC)

## Results Log

| Date | AAP Version | Node OS | Result | Notes |
|------|-------------|---------|--------|-------|
| 2026-08-07 | 2.6 AIO | RHEL 9 | Pass | Failed on `ee-supported` load (8.8G root); after resize to 64G and re-run, join completed (T-26-AIO-RERUN) |
