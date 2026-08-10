# S-041: Deprovision and Rejoin

## Metadata

- **Priority**: P1
- **Topology**: AIO + HN + EN (typical)
- **Status**: Tested (2.6)
- **TEST.md**: T-26-AIO-DEPROV-REJOIN

## Description

Remove collection-joined instances from Controller, optionally rebuild VMs (same names / new IPs), then join again with `add_node.yml`.

## Prerequisites

| Requirement | Value |
|-------------|-------|
| Controller | Containerized AAP 2.6+ with existing hop/EN to remove |
| SSH | Install user to controller and target nodes |
| Inventory | Updated `ansible_host` if IPs changed |

## Steps

1. On controller (install user):

   ```bash
   podman exec automation-controller-task \
     awx-manage deprovision_instance --hostname=hn-01.example.com
   podman exec automation-controller-task \
     awx-manage deprovision_instance --hostname=en-01.example.com
   podman exec automation-controller-task awx-manage list_instances
   ```

2. Confirm mesh is empty aside from the controller.
3. Rebuild VMs or keep hosts; update inventory IPs / SSH host keys as needed.
4. Run `playbooks/add_node.yml` (same pattern as [S-003](S-003-multi-hop.md) / [TEST.md](../../../TEST.md)).
5. Verify with [verification.md](../checklists/verification.md).

## Pass Criteria

- [ ] Same as S-003 / T-26-AIO-EN-VIA-HN (both green after settle)

## Related

- [S-003](S-003-multi-hop.md), [S-040](S-040-failure-recovery.md)
- [TROUBLESHOOTING.md](../../../docs/TROUBLESHOOTING.md) rollback section

## Results Log

| Date | AAP Version | Node OS | Result | Notes |
|------|-------------|---------|--------|-------|
| 2026-08-07 | 2.6 AIO | RHEL 9 | Pass | New IPs (`.62` hop / `.63` EN); playbook OK; both green (T-26-AIO-DEPROV-REJOIN) |
| 2026-08-10 | 2.6 AIO | RHEL 9 | Pass | Deprov + rejoin after DNS fix; see TEST.md / `.ignore/lab/runs/` (local) |
