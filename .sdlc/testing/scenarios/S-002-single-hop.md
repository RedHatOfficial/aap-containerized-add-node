# S-002: Single Hop Node

## Metadata

- **Priority**: P1
- **Topology**: AIO + HN (outbound dial)
- **Status**: Tested
- **TEST.md**: T-26-AIO-HN, T-27-AIO-HN

## Description

Add a hop node that peers to the controller (`receptor_type=hop`). Often validated as part of S-003 (EN via hop); isolated HN-only runs are preferred when claiming HN alone.

## Prerequisites

| Requirement | Value |
|-------------|-------|
| Controller | Containerized AAP 2.6+ AIO |
| Container | `automation-controller-task` running |
| SSH | Passwordless to controller and hop (install user) |
| Node disk | ≥ 32 GB (prefer 64 GB) |
| Node OS | RHEL 9.x (RHEL 10 hop still untested) |

## Inventory

```ini
[execution_nodes]
hn-01.example.com ansible_host=y.y.y.y ansible_user=ansible \
  receptor_type=hop \
  receptor_peers='["controller.example.com"]' \
  routable_hostname=hn-01.example.com
```

Use the mesh hostname the controller already knows (may differ from the SSH FQDN).

## Steps

Same installer command pattern as [TEST.md](../../../TEST.md). Verify with [verification.md](../checklists/verification.md) (`node_type=hop`, green heartbeat).

## Pass Criteria

- [ ] Playbook exit `0`
- [ ] Hop green; `node_type=hop`; recent heartbeat
- [ ] No unexpected restarts on existing mesh nodes (outbound dial)

## Related

- [S-003](S-003-multi-hop.md) — HN + EN via hop
- REQ-002 — Hop and execution node support

## Results Log

| Date | AAP Version | Node OS | Result | Notes |
|------|-------------|---------|--------|-------|
| 2026-08 | 2.6 AIO | RHEL 9 | Pass | T-26-AIO-HN — see TEST.md |
| 2026-08-10 | 2.7 AIO | RHEL 9 | Pass | Covered by T-27-AIO-EN-VIA-HN (hop → `aap27.lennysh.net`) |
